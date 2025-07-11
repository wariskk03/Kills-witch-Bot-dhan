import time
import requests
from datetime import datetime

from config import base_url, timeout, create_session, session as global_session

session = global_session

def make_requests(method, endpoint, param=None, payload=None):
    '''
    Handle requests error.
    And
    Parse the response.

    Args:
        method (str): Requests method get/post/put/delete.
        endpoint (str): url endpoint with (/) prefix.
        param (dict/json): Requesting parameters data.
        payload (dict/json): Uploading json data.

    Returns:
        dict/json: Parsed response containing error_code, error_type, error_message.
    '''
    global session, global_session
    url = f"{base_url}{endpoint}"
    for attempt in range(1, 4):
        try:
            if method == "get":
                response = session.get(url, params=param, timeout=timeout)
            elif method == "post":
                response = session.post(url, params=param, json=payload, timeout=timeout)
            elif method == "delete":
                response = session.delete(url, timeout=timeout)
            elif method == "put":
                response = session.put(url, json=payload, timeout=timeout)
            else:
                raise ValueError("Unsuported Method")
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError:
            print(f"📡 Connection error — network may be down or changed. Attempt {attempt}")
            
            session.close()           
            session = create_session() 
            global_session = session

            print(f"🔄 Retrying in {2 ** (attempt - 1)}s...")
            time.sleep(2 ** (attempt - 1))

        except requests.exceptions.HTTPError as e:
            print(f"📡 Unsuccessful response from API (Status: {e.response.status_code})")
            try:
                error_response_json = e.response.json()
                error_type = error_response_json.get('errorType')
                error_code = error_response_json.get('errorCode')
                error_message = error_response_json.get('errorMessage')
                remarks = {
                    'error_code': error_code,
                    'error_type' : error_type,
                    'error_message': error_message
                }
            except ValueError:
                # Fallback when error body is not JSON
                remarks = {
                    'error_code': None,
                    'error_type': "Non-JSON Error",
                    'error_message': e.response.text[:200]  # limit to avoid dumping HTML
                }

            print("🧾 API Error Details: ", remarks)

            if attempt == 3:
                raise Exception("All attempts failed!")
            print(f"🔄 Retrying in {2 ** (attempt - 1)}s...")
            time.sleep(2 ** (attempt - 1))
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Exception during making requests: {e}")
            if attempt == 3:
                raise Exception("All attempts failed!")
            print(f"🔄 Retrying in {2 ** (attempt - 1)}s...")
            time.sleep(2 ** (attempt - 1))
            
        except Exception as e:
            print(f"🐞 An unexpected exception occurred: {e}")
            if attempt == 3:
                raise Exception("All attempts failed!")
            print(f"🔄 Retrying in {2 ** (attempt - 1)}s...")
            time.sleep(2 ** (attempt - 1))


def calculate_pnl(positions):
    '''
    Calculate the Profit or loss.

    Args:
        positions (dict/json): json response from positions requests.

    Returns:
        float: profit or loss is returned.
    '''
    if not positions:
        return 0
    pnl = sum((pos.get("realizedProfit") or 0) + (pos.get("unrealizedProfit") or 0) for pos in positions)
    return pnl


def fetch_open_position(positions):
    '''
    Filter and fetch all open positions.

    Args:
        positions (dict/json): json response from positions requests.

    Returns:
        list of dict: list of dict of open positions.
    '''
    return [pos for pos in positions if pos.get("positionType") != "CLOSED"]


def close_positions(open_positions):
    '''
    Closes all open positions.

    Args:
        open_positions (list of dict): all open positions list to close.

    Returns:
        bool: True if all position is closed and False if not.
    '''
    success_count = 0
    for pos in open_positions:
        transactionType = "BUY" if pos.get("positionType") == "SHORT" else "SELL"
        payload = {
            "dhanClientId": pos.get("dhanClientId"),
            "correlationId": None,
            "transactionType": transactionType,
            "exchangeSegment": pos.get("exchangeSegment"),
            "productType": pos.get("productType"),
            "orderType": "MARKET",
            "validity": "DAY",
            "securityId": pos.get("securityId"),
            "quantity": abs(pos.get("netQty")),
            "disclosedQuantity": 0,
            "price": 0,
            "triggerPrice": 0,
            "afterMarketOrder": False,
            "amoTime": "OPEN",
            "boProfitValue": None,
            "boStopLossValue": None
        }
        try:
            make_requests(method="post", endpoint="/orders", payload=payload)
            success_count += 1
        except Exception as e:
            print(f"❌🔁 Error In Closing Positions:: {e}")
            
    return len(open_positions) == success_count


def fetch_pending_orders(orders):
    '''
    Filter and Fetch all open orders.

    Args:
        orders (dict/json): json response from orders list requests.
    
    returns:
        list: list of pending order IDs.
    '''
    return [ord["orderId"] for ord in orders if ord["orderStatus"] == "PENDING"]


def cancel_pending_orders(pending_order_ids_list):
    '''
    Cancels all pending orders available.

    Args:
        pending_order_ids_list (list): list of pending order ids

    Returns:
        bool: True if all orders are canceled else return False
    '''
    success_count = 0
    for ids in pending_order_ids_list[:]:
        try:
            make_requests(method="delete", endpoint=f"/orders/{ids}")
            success_count += 1
        except Exception as e:
            print(f"❌📦 Error In Cancelling Orders:: {e}")

    return len(pending_order_ids_list) == success_count
    

def kill_switch():
    '''
    Activates killswitch.

    Returns:
        prints killswitch status
    '''
    killswitch_param = {"killSwitchStatus":"ACTIVATE"}
    try:
        response = make_requests(method="post", endpoint="/killswitch", param=killswitch_param)
        status = response.get("killSwitchStatus", "UNKNOWN")

        if status == "Kill Switch Activated":
            print(f"✅ KILL SWITCH STATUS: {status}")
        else:
            print(f"⚠️ Unexpected KILL SWITCH STATUS: {status}")

    except Exception as e:
        print(f"❌ Error in Activating Killswitch: {e}")


def deactivate_killswitch():
    '''
    deactivates the killswitch
    '''
    try:

        kill_switch_status = make_requests(method="get", endpoint="/killswitch").get("killSwitchStatus")

        if kill_switch_status == "ACTIVE":
            param = {"killSwitchStatus":"DEACTIVATE"}
            response = make_requests(method="post", endpoint="/killswitch", param=param)
            status = response.get("killSwitchStatus") 

            if status == "Kill Switch Deactivated":
                print("🟢 Kill Switch DEACTIVATED!")
            else:
                print(f"⚠️ Unexpected Deactivating Kill Switch Status: {status}")

    except Exception as e:
        print(f"❌ Error in Deactivating Killswitch: {e}")


def trading_hour_over():
    '''
    Check if trading hour is over.

    Returns:
        bool: True if time is more than the trading hour else False
    '''
    now = datetime.now()
    market_close = now.replace(hour=15, minute=29, second=0, microsecond=0)
    return now >= market_close


def traded_orders(orders_list):
    '''
    Returns all completed orders

    Args:
        orders_list (dict/json): orders response from orders requests

    Returns:
        list: List of traded or completed orders
    '''
    return [ord for ord in orders_list if ord["orderStatus"] == "TRADED"]


def calculate_trade_turnover(traded_orders_list):
    '''
    Gives the total turnover value 

    Args:
        traded_orders_list (list): list of traded orders

    Returns:
        int: total turnover value 
    '''
    trade_turnover = 0
    for ord in traded_orders_list:
        quantity = ord["filledQty"]
        traded_price = ord["averageTradedPrice"]
        trade_turnover += (traded_price*quantity)
    return trade_turnover
    

def calculate_bokerage(traded_orders_list, turnover, brokerage=20):
    '''
    Calculate total brokerages
    '''
    total_brokerage = brokerage*len(traded_orders_list)
    etc = turnover * 0.00053
    stt = (turnover / 2) * 0.0005
    sebi = turnover * 0.000001
    ipft = turnover * 0.000001
    stamp = (turnover / 2) * 0.00003
    gst = (total_brokerage + etc) * 0.18

    total_charges = total_brokerage+etc+stt+sebi+ipft+stamp+gst
    return total_charges
    
