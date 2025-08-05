import os
import time

from config import load_config
from utils import *
from log_config import log_config

config = load_config()
DAILY_RISK = config["daily_risk"]
polling_interval = config["polling_interval"]

logger = log_config(__name__)

def run_killswitch_bot():
    '''
    Steps in while loop:
        -> make positions requests
        -> check PNL 
        -> check daily risk conditions (re-run with sleep time if False)
        -> make orders requests
        -> get open positions
        -> close open positions
        -> get pending orders
        -> cancel pending orders
        -> set closed_flag and canceled_flag True if only all positions and orders are closed and canceled
        -> check if all flags are True
        -> Activate killswitch 
        -> break
        -> run until Trading hours
    '''
    previous_order_len = 0
    previous_brokerage = 0
    while True:
        try:
            orders = make_requests(method="get", endpoint="/orders")
            positions = make_requests(method="get", endpoint="/positions")

            if len(orders) != previous_order_len:
                traded = traded_orders(orders)
                turnover = calculate_trade_turnover(traded)
                previous_brokerage = calculate_bokerage(traded, turnover)
                previous_order_len = len(orders)

            PNL = calculate_pnl(positions) - previous_brokerage

            os.system("clear")
            logger.debug(f"📊 running-pnl: {round(PNL, 2)}")
            if PNL < float(DAILY_RISK):
                logger.info("🚨 ACTIVATING KILLSWITCH!!!")

                logger.info("📉 Closing Positions")
                open_positions = fetch_open_position(positions)
                close_positions(open_positions)

                logger.info("📋 Canceling Orders")
                pending_orders = fetch_pending_orders(orders)
                cancel_pending_orders(pending_orders)

                try:
                    logger.info("🫡 Final Check")

                    orders = make_requests(method="get", endpoint="/orders")
                    pending_orders = fetch_pending_orders(orders)

                    positions = make_requests(method="get", endpoint="/positions")
                    open_positions = fetch_open_position(positions)

                    closed_flag = not len(pending_orders)
                    canceled_flag = not len(open_positions)

                except Exception as e:
                    logger.exception("⚠️ Error In Getting Positions or Orders list")
                    time.sleep(1)

                if closed_flag and canceled_flag:
                    kill_switch()
                    
                    try:
                        kill_switch_status = make_requests(method="get", endpoint="/killswitch").get("killSwitchStatus")
                    except Exception as e:
                        logger.exception("⚠️ Error in getting killswitch status")

                    if kill_switch_status == "ACTIVE":
                        deactivate_killswitch()
                        kill_switch()
                        break
                    else:
                        continue

                else:
                    logger.warning("Positions or orders are still open")

            if trading_hour_over():
                logger.info("⏰ Trading hours over. Exiting bot.")
                break

            time.sleep(polling_interval)
        
        except Exception as e:
            logger.exception("⚠️ Error In Getting Positions or Orders list")
            break
        