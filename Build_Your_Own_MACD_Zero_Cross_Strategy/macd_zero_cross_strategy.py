
import mt5_lib # <- Import your connection to MetaTrader 5
import indicator_lib # <- Import your connection to an indicator library


# Function to define the MACD Zero Cross Strategy
def macd_zero_cross_strategy(symbol, timeframe, macd_fast=12, macd_slow=26, macd_signal=9, exchange="mt5"):
    """
    Function to define the MACD Zero Cross Strategy. Default settings for the MACD Technical Indicator are provided.
    These can be modified.
    :param symbol: string of the symbol to be retrieved
    :param timeframe: string of the timeframe to be queried
    :param macd_fast: integer of the fast EMA Size. Default = 12.
    :param macd_slow: integer of the slow EMA Size. Default = 26.
    :param macd_signal: integer of the MACD Signal size. Default = 9.
    :param exchange: string of the exchange used to query data
    :return: dataframe with trade signals
    """

    ### Pseudo Code ###
    # 1: Get data -> get_data()
    # 2: Calculate the indicators -> calc_indicators()
    # 3: Calculate the signal -> calc_signals()
    # 4: Not Covered in this episode: Make Trades

    # Step 1: Retrieve Data
    data = get_data(
        symbol=symbol,
        timeframe=timeframe,
        exchange=exchange
    )
    # Step 2: Calculate indicators
    data = calc_indicators(
        dataframe=data,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )
    # Step 3: Calculate signals
    data = calc_signal(
        dataframe=data
    )
    # Return outcome
    return data


# Function to retrieve dta for the strategy
def get_data(symbol, timeframe, exchange="mt5"):
    """
    Function to retrieve data from MT5. Data is in the form of candlesticks and should include a 'close' column
    in the dataframe
    :param symbol: string of the symbol to be analyzed
    :param timeframe: string of the timeframe to be analyzed
    :param exchange: string of the exchange to be queried
    :return: dataframe
    """
    if exchange == "mt5":
        # Retrieve data
        data = mt5_lib.get_candlesticks(
            symbol=symbol,
            timeframe=timeframe,
            number_of_candles=1000
        )
    # Add in extra exchanges here as needed
    # If exchange not covered in code, raise an error
    else:
        raise ValueError("Exchange not supported")
    # Return dataframe
    return data


# Function to calculate indicators for the strategy
def calc_indicators(dataframe, macd_fast=12, macd_slow=26, macd_signal=9):
    """
    Function to calculate the indicators for the strategy. Input dataframe must contain a column with 'close' values
    included.
    :param dataframe: dataframe of symbol data to be analyzed
    :param macd_fast: integer of the fast EMA Size. Default 12.
    :param macd_slow: integer of the slow EMA Size. Default 26.
    :param macd_signal: integer of the signal EMA size. Default 9.
    :return: dataframe with indicators
    """
    # Calculate the MACD Indicator
    dataframe = indicator_lib.calc_macd(
        dataframe=dataframe,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )
    # Calculate the MACD Zero Cross Indicator
    dataframe = indicator_lib.calc_zero_cross(
        dataframe=dataframe,
        column="macd"
    )
    # Return dataframe
    return dataframe


# Function to calculate a trade signal
def calc_signal(dataframe):
    """
    Function to calculate trade signals
    :param dataframe: dataframe of data to be analyzed
    :return: dataframe with trade signals
    """
    # Add columns for order_type, stop_price, stop_loss, and take_profit
    dataframe["order_type"] = ""
    dataframe["stop_price"] = 0.0
    dataframe["stop_loss"] = 0.0
    dataframe["take_profit"] = 0.0
    # Skip the first row as otherwise index - 1 will fail
    start_index = dataframe.index[0]
    # Iterate through the dataframe. If 'zero_cross' is true, determine if MACD is above or below
    for index, row in dataframe.iterrows():
        # Check to make sure first row of dataframe has been skipped
        if index > start_index:
            if row["zero_cross"]:
                # Find Sell Stops
                if row["macd"] < 0:
                    # Set the order type
                    order_type = "SELL_STOP"
                    # Stop Price is previous candles LOW
                    stop_price = dataframe.loc[index-1, "low"]
                    # Stop Loss is previous candles high
                    stop_loss = dataframe.loc[index-1, "high"] # <- Modify this to modify stop_loss
                    # Distance is difference between stop loss and stop price subtracted from stop_price (i.e. 1:1)
                    distance = stop_loss - stop_price # <- Modify this to modify take profit ratio
                    take_profit = stop_price - distance
                else:
                    # Order type is a BUY STOP
                    order_type = "BUY_STOP"
                    # Stop Price is the previous candles high
                    stop_price = dataframe.loc[index-1, "high"]
                    # Stop Loss is the previous candles low
                    stop_loss = dataframe.loc[index-1, "low"] # <- Modify this to modify stop_loss
                    # Take Profit is 1:1
                    distance = stop_price - stop_loss # <- Modify this to modify take profit ratio
                    take_profit = stop_price + distance
                # Update the dataframe with the values
                dataframe.at[index, "order_type"] = order_type
                dataframe.at[index, "stop_price"] = stop_price
                dataframe.at[index, "stop_loss"] = stop_loss
                dataframe.at[index, "take_profit"] = take_profit
    # Return completed dataframe
    return dataframe
