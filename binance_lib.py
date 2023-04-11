import pandas
from binance.spot import Spot as Client
from configparser import ConfigParser


# Function to retrieve account information
def check_binance_working(project_settings):
    """
    Function to check that Binance is working. This is done by retrieving account information.
    :param project_settings: JSON object with project_settings
    :return: Boolean True/False
    """
    # Get the API_Key and API_Secret for the Spot Client
    api_key, api_secret = get_api_keys(project_settings=project_settings)
    # Instantiate the Spot Client
    spot_client = Client(api_key, api_secret)
    # Get the account status
    account = spot_client.account_status()
    # Check to see if the data returns Normal
    if account['data'] == "Normal":
        return True
    # You can put handling for other status returns if you want
    return False



# Function to get the API Keys
def get_api_keys(project_settings):
    """
    Function to retrieve the API keys (Public, Secret) from Binance using the Binance Config Parser.

    :param project_settings: JSON object with project_settings
    :return: API Key, Secret Key
    """
    # Instantiate the ConfigParser
    config = ConfigParser()
    # Read the INI file
    config.read(project_settings['binance']['config_location'])
    # Return the config
    return config["keys"]["api_key"], config["keys"]["api_secret"]


# Create a function to get the candles from Binance
def get_candlesticks(symbol, timeframe, number_of_candles):
    """
    Function to retrieve candlestick data from Binance.
    Documentation on Binance Candlesticks (KLines): https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#klinecandlestick-data
    :param symbol: string of the symbol to retrieve
    :param timeframe: string of the timeframe of the candles to be retrieved
    :param number_of_candles: integer of the number of candles to retrieve
    :return: dataframe with the candlesticks
    """
    # Psuedocode
    # 1. Set the query timeframe so it is consistent with the timeframe used for other exchanges
    # 2. Ensure that no more than 1000 candles retrieved (hard limit from Binance)
    # 3. Retrieve the candles
    # 4. Format the candles into a dataframe, and label columns accordingly
    # 5. Return the dataframe

    # Step 1: Convert the timeframe into a Binance friendly format
    timeframe = set_query_timeframe(timeframe=timeframe)
    # Step 2: Make sure that no more than 1000 candles are being retrieved as this is a hard limit from Binance
    if number_of_candles > 1000:
        raise ValueError("Number of candles cannot be greater than 1000")
    # Step 3: Retrieve the candles
    # Instantiate the Spot Client
    spot_client = Client() #<- No API keys needed for this request
    # Retrieve the candles / OHLC data
    candles = spot_client.klines(
        symbol=symbol,
        interval=timeframe,
        limit=number_of_candles
    )
    # Convert to a dataframe
    candles_dataframe = pandas.DataFrame(candles)
    # Step 4: Format the columns of the Dataframe.
    # Documentation: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#klinecandlestick-data
    candles_dataframe.columns = ["time", "open", "high", "low", "close", "volume", "close Time", "Quote Asset Volume",
                                "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume",
                                 "Ignore"]
    # Add a human time column which is based on a DateTime fo the 'time' column
    candles_dataframe['human_time'] = pandas.to_datetime(candles_dataframe['time'], unit='ms')
    # Make sure that the "open", "high", "low", "close", "volume" columns are floats
    candles_dataframe[["open", "high", "low", "close", "volume"]] = candles_dataframe[["open", "high", "low", "close", "volume"]].astype(float)
    # Step 5: Return the dataframe
    return candles_dataframe


# Function to convert a provided timeframe into a Binance friendly format
def set_query_timeframe(timeframe):
    """
    Function to implement a conversion from a common timeframe format to a Binance specific format. Note that the
    function implements a pseudo switch statement as Python version < 3.10 do not include switch as an option.
    List of timeframes Binance supports: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#enum-definitions
    :param timeframe: string of the timeframe being converted
    :return: string of Binance friendly format
    """
    if timeframe == "S1":
        return "1s"
    elif timeframe == "M1":
        return "1m"
    elif timeframe == "M3":
        return "3m"
    elif timeframe == "M5":
        return "5m"
    elif timeframe == "M15":
        return "15m"
    elif timeframe == "M30":
        return "30m"
    elif timeframe == "H1":
        return "1h"
    elif timeframe == "H2":
        return "2h"
    elif timeframe == "H4":
        return "4h"
    elif timeframe == "H6":
        return "6h"
    elif timeframe == "H8":
        return "8h"
    elif timeframe == "H12":
        return "12h"
    elif timeframe == "D1":
        return "1d"
    elif timeframe == "D3":
        return "3d"
    elif timeframe == "W1":
        return "1w"
    elif timeframe == "MN1":
        return "1M"
    else:
        print(f"Incorrect timeframe provided. {timeframe}")
        raise ValueError("Input the correct timeframe")


# Function to make a trade with Binance
def place_order(order_type, symbol, quantity, stop_loss, stop_price, take_profit, comment, project_settings, direct=False):
    """
    Function to place an order on Binance. Checks to see if the order is valid first.
    Documentation:
    https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#new-order--trade
    https://github.com/binance/binance-connector-python/blob/master/examples/spot/trade/new_order.py
    https://github.com/binance/binance-connector-python/blob/master/examples/spot/trade/new_order_testing.py
    :param order_type: string of the order type. Options are "BUY_STOP" or "SELL_STOP"
    :param symbol: string of the symbol to be traded. Must be Binance compatible.
    :param quantity: Float of the quantity to be traded.
    :param stop_loss: Float of the stop loss
    :param stop_price: Float of the stop price
    :param take_profit: Float of the take profit
    :param comment: string of the comment for the trade
    :param project_settings: dictionary of the project settings
    :param direct: Boolean as to if the order check should be bypassed. Default is False.
    :return: Outcome
    """
    # Psuedocode
    # 1. Check to see if the order is valid
    # 2. Place the order
    # 3. Return the outcome

    # Make sure that all the inputs are correct
    if order_type not in ["BUY_STOP", "SELL_STOP"]:
        raise ValueError("Incorrect order type provided. Must be 'BUY_STOP' or 'SELL_STOP'")
    if not isinstance(symbol, str):
        raise ValueError("Incorrect symbol provided. Must be a string")
    if not isinstance(quantity, float):
        float(quantity)
    if not isinstance(stop_loss, float):
        float(stop_loss)
    if not isinstance(stop_price, float):
        float(stop_price)
    if not isinstance(take_profit, float):
        float(take_profit)
    if not isinstance(comment, str):
        raise ValueError("Incorrect comment provided. Must be a string")
    if not isinstance(direct, bool):
        raise ValueError("Incorrect direct provided. Must be a boolean")
    # Get Keys for the API
    api_key, secret_key = get_api_keys(project_settings=project_settings)
    # Set up the API Client
    client = Client(api_key, secret_key)
    # Set up the parameters dictionary
    parameters = {
        "symbol": symbol,
        "type": "STOP_LOSS_LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "stopPrice": stop_price,
        "price": stop_price
    }
    # Apply the correct side based upon the order type
    if order_type == "BUY_STOP":
        parameters["side"] = "BUY"
    elif order_type == "SELL_STOP":
        parameters["side"] = "SELL"

    if direct:
        try:
            response = client.new_order(**parameters)
            print(response)
        except Exception as e:
            print("Order Failed")
            print(e)
            response = e
        return response
    else:
        # Test the order
        try:
            response = client.new_order_test(**parameters)
            print(response)
        except Exception as e:
            print("Order is not valid")
            print(e)
            response = e

        # If the order is valid, place the order
        if response == {}:
            # Place the order. Use the same function but with the direct parameter set to True
            response = place_order(
                order_type=order_type,
                symbol=symbol,
                quantity=quantity,
                stop_loss=stop_loss,
                stop_price=stop_price,
                take_profit=take_profit,
                comment=comment,
                project_settings=project_settings,
                direct=True
            )

    # Step 3: Return the outcome
    return response


# Function to get a list of current orders on Binance
def get_open_orders(project_settings, symbol):
    """
    Function to get a list of current orders on Binance
    Documentation:
    https://github.com/binance/binance-connector-python/blob/master/examples/spot/trade/get_orders.py
    https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#all-orders-user_data
    :param project_settings: json dictionary of the project settings
    :param symbol: string of the symbol to get orders on. Default is none, which will return all orders
    :return: dataframe of the order(s)
    """
    # Psuedocode
    # 1. Get the API keys
    # 2. Set up the client
    # 3. Get the orders
    # 4. Return the orders

    # Step 1: Get the API keys
    api_key, secret_key = get_api_keys(project_settings=project_settings)

    # Step 2: Set up the client
    client = Client(api_key, secret_key)

    # Step 3: Get the orders
    # If the symbol is not provided, get all orders
    orders = client.get_open_orders(symbol=symbol)

    # Step 4: Return the orders
    return orders


# Function to cancel an order on Binance
def cancel_order(project_settings, symbol, order_id):
    """
    Function to cancel an order on Binance
    Documentation: https://github.com/binance/binance-connector-python/blob/master/examples/spot/trade/cancel_order.py
    :param project_settings: json dictionary of the project settings
    :param symbol: string of the symbol to cancel the order on
    :param order_id: string of the order id to cancel the order on
    :return: True if the order was cancelled, False if not
    """
    # Psuedocode
    # 1. Get the API keys
    # 2. Set up the client
    # 3. Cancel the order
    # 4. Return the outcome

    # Step 1: Get the API keys
    api_key, secret_key = get_api_keys(project_settings=project_settings)

    # Step 2: Set up the client
    client = Client(api_key, secret_key)

    # Step 3: Cancel the order
    try:
        response = client.cancel_order(symbol=symbol, orderId=order_id)
        print(response)
        outcome = True
    except Exception as e:
        print(e)
        outcome = False

    # Step 4: Return the outcome
    return outcome
