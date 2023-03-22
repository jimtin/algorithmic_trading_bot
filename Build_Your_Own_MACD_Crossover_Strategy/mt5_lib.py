import MetaTrader5
import pandas


# Function to start MetaTrader 5
def start_mt5(project_settings):
    """
    Function to start MetaTrader 5
    :param project_settings: json object with username, password, server, file location of terminal64.exe
    :return: Boolean. True = started, False = not started
    """
    # Ensure that all variables are set/formatted to the correct type
    username = project_settings['mt5']['username']
    username = int(username)
    password = project_settings['mt5']['password']
    server = project_settings['mt5']['server']
    mt5_pathway = project_settings['mt5']['mt5_pathway']

    # Attempt to initialize MT5
    mt5_init = False
    try:
        mt5_init = MetaTrader5.initialize(
            login=username,
            password=password,
            server=server,
            path=mt5_pathway
        )
    # Handle any errors
    except Exception as e:
        print(f"Error initializing MetaTrader 5: {e}")
        # Return False
        mt5_init = False

    # If MT5 initialized, attempt to login to MT5
    mt5_login = False
    if mt5_init:
        # Attempt login
        try:
            mt5_login = MetaTrader5.login(
                login=username,
                password=password,
                server=server
            )
        # Handle exception
        except Exception as e:
            print(f"Error logging into MetaTrader 5: {e}")
            mt5_login = False

    # Return the outcome to the user
    if mt5_login:
        return True
    # Default outcome
    return False


# Function to initialize a symbol on MT5
def initialize_symbol(symbol):
    """
    Function to initialize a symbol on MT5. Assumes that MT5 has already been started.
    :param symbol: string of symbol. Note that most MT5 brokers denote a 'raw' symbol differently from a standard symbol
    :return: Boolean. True if initialized. False if not.
    """
    # Step 1: Check is symbol exists on 'your' MT5
    all_symbols = MetaTrader5.symbols_get()
    # Create a list to store all symbol names
    symbol_names = []
    # Add all symbol names to the list
    for sym in all_symbols:
        symbol_names.append(sym.name)

    # Check the symbol string to see if it exists in the list of names
    if symbol in symbol_names:
        # If symbol exists, attempt to initialize
        try:
            MetaTrader5.symbol_select(symbol, True) # <- Arguments cannot be declared here or an error will be thrown.
            return True
        except Exception as e:
            print(f"Error enabling {symbol}. Error: {e}")
            # Great place for some custom error handling ;)
            return False
    else:
        print(f"Symbol {symbol} does not exist on this version of MT5. Update symbol name.")
        return False


# Function to query historic candlestick data from MT5
def get_candlesticks(symbol, timeframe, number_of_candles):
    """
    Function to retrieve a user-defined number of candles from MetaTrader 5. Initial upper range set to
    50,000 as more requires changes to MetaTrader 5 defaults.
    :param symbol: string of the symbol being retrieved
    :param timeframe: string of the timeframe being retrieved
    :param number_of_candles: integer of number of candles to retrieve. Limited to 50,000
    :return: dataframe of the candlesticks
    """
    # Check that the number of candles is <= 50,000
    if number_of_candles > 50000:
        raise ValueError("No more than 50000 candles can be retrieved at this time")
    # Convert the timeframe into MT5 friendly format
    mt5_timeframe = set_query_timeframe(timeframe=timeframe)
    # Retrieve the data
    candles = MetaTrader5.copy_rates_from_pos(symbol, mt5_timeframe, 1, number_of_candles)
    # Convert to a dataframe
    dataframe = pandas.DataFrame(candles)
    return dataframe


# Function to convert MT5 timeframe string into MT5 object
def set_query_timeframe(timeframe):
    """
    Function to implement a conversion from a user-friendly timeframe string into a MT5 friendly object. Note that the
    function implements a Pseudo switch as Python version < 3.10 do not contain 'switch' functionality.
    :param timeframe: string of the timeframe
    :return: MT5 Timeframe Object
    """
    if timeframe == "M1":
        return MetaTrader5.TIMEFRAME_M1
    elif timeframe == "M2":
        return MetaTrader5.TIMEFRAME_M2
    elif timeframe == "M3":
        return MetaTrader5.TIMEFRAME_M3
    elif timeframe == "M4":
        return MetaTrader5.TIMEFRAME_M4
    elif timeframe == "M5":
        return MetaTrader5.TIMEFRAME_M5
    elif timeframe == "M6":
        return MetaTrader5.TIMEFRAME_M6
    elif timeframe == "M10":
        return MetaTrader5.TIMEFRAME_M10
    elif timeframe == "M12":
        return MetaTrader5.TIMEFRAME_M12
    elif timeframe == "M15":
        return MetaTrader5.TIMEFRAME_M15
    elif timeframe == "M20":
        return MetaTrader5.TIMEFRAME_M20
    elif timeframe == "M30":
        return MetaTrader5.TIMEFRAME_M30
    elif timeframe == "H1":
        return MetaTrader5.TIMEFRAME_H1
    elif timeframe == "H2":
        return MetaTrader5.TIMEFRAME_H2
    elif timeframe == "H3":
        return MetaTrader5.TIMEFRAME_H3
    elif timeframe == "H4":
        return MetaTrader5.TIMEFRAME_H4
    elif timeframe == "H6":
        return MetaTrader5.TIMEFRAME_H6
    elif timeframe == "H8":
        return MetaTrader5.TIMEFRAME_H8
    elif timeframe == "H12":
        return MetaTrader5.TIMEFRAME_H12
    elif timeframe == "D1":
        return MetaTrader5.TIMEFRAME_D1
    elif timeframe == "W1":
        return MetaTrader5.TIMEFRAME_W1
    elif timeframe == "MN1":
        return MetaTrader5.TIMEFRAME_MN1
    else:
        print(f"Incorrect timeframe provided. {timeframe}")
        raise ValueError("Input the correct timeframe")


# Function to place an order on MetaTrader 5
def place_order(order_type, symbol, volume, stop_loss, take_profit, comment, stop_price, direct=False):
    """
    Function to place an order on MetaTrader 5. Function checks the order first (best practice), then places trade if
    order check returns true.
    :param order_type: string. Options are SELL_STOP, BUY_STOP
    :param symbol: string of the symbol to be traded
    :param volume: string or float of the volume to be traded
    :param stop_loss: string or float of Stop Loss price
    :param take_profit: string or float of Take Profit price
    :param comment: string of the comment. Used to track different algorithms on same MT5 account
    :param stop_price: string or float of Stop Price
    :param direct: Boolean. Defaults to False. When true, will bypass order check
    :return: Trade Outcome
    """
    # Make sure volume, stop_loss, take_profit and stop prices are in correct format (float)
    volume = float(volume)
    # Volume can only be two decimal places
    #### Note that this may mess up your volume calculations for small accounts
    volume = round(volume, 2)
    # Stop Loss
    stop_loss = float(stop_loss)
    # Stop loss should be no more than 4 decimal places
    stop_loss = round(stop_loss, 4)
    # Take Profit should be a float, no more than 4 decimal places
    take_profit = float(take_profit)
    take_profit = round(take_profit, 4)
    # Stop Price should be a float, no more than 4 decimal places
    stop_price = float(stop_price)
    stop_price = round(stop_price, 4)
    # Set up the order request dictionary object. This will be the request sent to MT5
    request = {
        "symbol": symbol,
        "volume": volume,
        "sl": stop_loss,
        "tp": take_profit,
        "type_time": MetaTrader5.ORDER_TIME_GTC,
        "comment": comment
    }
    # Create the order type based on values
    if order_type == "SELL_STOP":
        # Update the request
        request['type'] = MetaTrader5.ORDER_TYPE_SELL_STOP
        request['action'] = MetaTrader5.TRADE_ACTION_PENDING
        request['type_filling'] = MetaTrader5.ORDER_FILLING_RETURN
        if stop_price <= 0:
            raise ValueError("Stop price cannot be zero")
        else:
            request['price'] = stop_price
    elif order_type == "BUY_STOP":
        # Update the request
        request['type'] = MetaTrader5.ORDER_TYPE_BUY_STOP
        request['action'] = MetaTrader5.TRADE_ACTION_PENDING
        request['type_filling'] = MetaTrader5.ORDER_FILLING_RETURN
        # Check the stop price
        if stop_price <= 0:
            raise ValueError("Stop Price cannot be zero")
        else:
            request['price'] = stop_price
    else:
        # An order type which is not part of the current functionality has been provided
        raise ValueError(f"Unsupported order type {order_type} provided")

    # If direct is True, go straight to adding the order
    if direct:
        # Send the order to MT5 terminal
        order_result = MetaTrader5.order_send(request)
        # Notify based on the return outcomes
        if order_result[0] == 10009:
            print(f"Order for {symbol} successful")
            return order_result[2]
        # Notify the user if AutoTrading has been left on in MetaTrader 5
        elif order_result[0] == 10027:
            print("Turn off AlgoTrading on MT5 Terminal")
            raise Exception("Turn off Algo Trading on MT5 Terminal")
        elif order_result[0] == 10015:
            print(f"Invalid price for {symbol}. Price: {stop_price}")
        elif order_result[0] == 10016:
            print(f"Invalid stops for {symbol}. Stop Loss: {stop_loss}")
        elif order_result[0] == 10014:
            print(f"Invalid volume for {symbol}. Volume: {volume}")
            # You can put custom errors in here if needed
        # Default
        else:
            print(f"Error lodging order for {symbol}. Error code: {order_result[0]}. Order Details: {order_result}")
            raise Exception(f"Unknown error lodging order for {symbol}")
    else:
        # Check the order
        result = MetaTrader5.order_check(request)
        # If check passes, place an order
        if result[0] == 0:
            print(f"Order check for {symbol} successful. Placing order.")
            # Place the order using recursion
            place_order(
                order_type=order_type,
                symbol=symbol,
                volume=volume,
                stop_price=stop_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment=comment,
                direct=True
            )
        # Let user know if an invalid price has been passed
        elif result[0] == 100015:
            print(f"Invalid price for {symbol}. Price: {stop_price}")
        # Default
        else:
            print(f"Order check failed. Details: {result}")


# Function to Cancel an order on MT5
def cancel_order(order_number):
    """
    Function to cancel an order identified by an order number
    :param order_number: int representing the order number from MT5
    :return: Boolean. True = cancelled. False == Not Cancelled.
    """
    # Create the request
    request = {
        "action": MetaTrader5.TRADE_ACTION_REMOVE,
        "order": order_number,
        "comment": "order removed"
    }
    # Attempt to send the order to MT5
    try:
        order_result = MetaTrader5.order_send(request)
        if order_result[0] == 10009:
            print(f"Order {order_number} successfully cancelled")
            return True
        # You can put custom error handling if needed
        else:
            print(f"Order {order_number} unable to be cancelled")
            return False
    except Exception as e:
        # This represents an issue with MetaTrader 5 terminal, so stop
        print(f"Error cancelling order {order_number}. Error: {e}")
        raise Exception


# Function to retrieve all currently open orders on MetaTrader 5
def get_all_open_orders():
    """
    Function to retrieve all open orders from MetaTrader 5
    :return: list of open orders
    """
    return MetaTrader5.orders_get()


# Function to retrieve a filtered list of open orders from MT5
def get_filtered_list_of_orders(symbol, comment):
    """
    Function to retrieve a filtered list of open orders from MT5. Filtering is performed
    on symbol and comment
    :param symbol: string of the symbol being traded
    :param comment: string of the comment
    :return: (filtered) list of orders
    """
    # Retrieve a list of open orders, filtered by symbol
    open_orders_by_symbol = MetaTrader5.orders_get(symbol)
    # Check if any orders were retrieved (there may be none)
    if open_orders_by_symbol is None or len(open_orders_by_symbol) == 0:
        return []

    # Convert the retrieved orders into a dataframe
    open_orders_dataframe = pandas.DataFrame(
        list(open_orders_by_symbol),
        columns=open_orders_by_symbol[0]._asdict().keys()
    )
    # From the open orders dataframe, filter orders by comment
    open_orders_dataframe = open_orders_dataframe[open_orders_dataframe['comment'] == comment]
    # Create a list to store the open order numbers
    open_orders = []
    # Iterate through the dataframe and add order numbers to the list
    for order in open_orders_dataframe['ticket']:
        open_orders.append(order)
    # Return the open orders
    return open_orders


# Function to cancel orders based upon filters
def cancel_filtered_orders(symbol, comment):
    """
    Function to cancel a list of filtered orders. Based upon two filters: symbol and comment string.
    :param symbol: string of symbol
    :param comment: string of the comment
    :return: Boolean. True = orders cancelled, False = issue with cancellation
    """
    # Retreive a list of the orders based upon the filter
    orders = get_filtered_list_of_orders(
        symbol=symbol,
        comment=comment
    )
    if len(orders) > 0:
        # Iterate through and cancel
        for order in orders:
            cancel_outcome = cancel_order(order)
            if cancel_outcome is not True:
                return False
        # At conclusion of iteration, return true
        return True
    else:
        return True

