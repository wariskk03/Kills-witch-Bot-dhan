import os
import time
from config import DAILY_RISK, polling_interval, session
from utils import make_requests, calculate_pnl, fetch_open_position, close_positions, fetch_pending_orders, cancel_pending_orders, trading_hour_over, kill_switch, calculate_bokerage, traded_orders, calculate_trade_turnover, deactivate_killswitch


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
            print("📊 running-pnl: ", round(PNL, 2))
            if PNL < float(DAILY_RISK):
                print("🚨 ACTIVATING KILLSWITCH!!!")

                print("📉 Closing Positions")
                open_positions = fetch_open_position(positions)
                closed_flag = close_positions(open_positions)

                print("📋 Canceling Orders")
                pending_orders = fetch_pending_orders(orders)
                canceled_flag = cancel_pending_orders(pending_orders)

                if closed_flag and canceled_flag:
                    kill_switch()
                    deactivate_killswitch()
                    kill_switch()
                    session.close()
                    break

            if trading_hour_over():
                print("⏰ Trading hours over. Exiting bot.")
                break

            time.sleep(polling_interval)
        
        except Exception as e:
            print("⚠️ Error In Getting Positions or Orders list::", e)
            time.sleep(1)
