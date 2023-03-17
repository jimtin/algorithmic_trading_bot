import mt5_lib
import indicator_lib


# Main MACD Crossover Strategy Function
def macd_crossover_strategy(symbol, timeframe, macd_fast=12, macd_slow=26, macd_signal=9, exchange="mt5"):
    """
    Main MACD Crossover Strategy Function
    :param symbol: symbol to be analyzed
    :param timeframe: timeframe to analyze
    :param macd_fast: fast EMA size
    :param macd_slow: slow EMA size
    :param macd_signal: signal EMA size
    :return: trade signal dataframe
    """
    ### Pseudo Code ###
    # 1. Retreive data -> get_data()
    # 2. Calculate indicators -> calc_indicators()
    # 3. Determine trades -> det_trade()
    # 4. Make trade -> make_trade()

    # Step 1: Retrieve data
    data = get_data(
        symbol=symbol,
        timeframe=timeframe,
        exchange=exchange
    )
    # Step 2: Pass data to calculate indicators
    data = calc_indicators(
        dataframe=data,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )
    # Step 3: Calculate trade events
    data = calc_signal(
        dataframe=data
    )
    # Return outcome to user
    return data


# Function to retrieve data for strategy
def get_data(symbol, timeframe, exchange="mt5"):
    """
    Function to retrieve data from MT5. Data is in the form of candlesticks and should be returned as a
    dataframe
    :param symbol: string of the symbol to be retrieved
    :param timeframe: string of the timeframe to be queried
    :return: dataframe
    """
    if exchange == "mt5":
        # Note, this function can be expanded to retrieve data from other exchanges also.
        data = mt5_lib.query_historic_data(symbol=symbol, timeframe=timeframe, number_of_candles=1000)
    # Add other exchanges here if needed
    else:
        raise ValueError("Exchange not supported")
    # Return dataframe
    return data


# Function to calculate indicators
def calc_indicators(dataframe, macd_fast=12, macd_slow=26, macd_signal=9):
    """
    Function to calculate indicators for the strategy
    :param dataframe: dataframe of data to be analyzed
    :param macd_fast: fast EMA size
    :param macd_slow: slow EMA size
    :param macd_signal: signal EMA size
    :return: dataframe with indicators
    """
    # Calculate MACD Indicator
    dataframe = indicator_lib.calc_macd(
        dataframe=dataframe,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )
    # Calculate MACD Crossover Indicator
    dataframe = indicator_lib.calc_crossover(
        dataframe=dataframe,
        column_one="macd",
        column_two="macd_signal"
    )
    # Return dataframe
    return dataframe


# Function to calculate trade signals
def calc_signal(dataframe):
    """
    Function to calculate trade signals
    :param dataframe: dataframe of data to be analyzed
    :return: dataframe with trade signals
    """
    # Add columns for order_type, stop price, stop loss, and take profit
    dataframe['order_type'] = ""
    dataframe['stop_price'] = 0
    dataframe['stop_loss'] = 0
    dataframe['take_profit'] = 0
    # Iterate through dataframe. If 'crossover' column is true, determine which direction the cross occurred
    for index, row in dataframe.iterrows():
        # Set the signal variable
        signal = 0
        # Check if crossover occurred
        if row['crossover']:
            # Check if MACD is above signal line
            if row['macd'] > row['macd_signal']:
                # Set signal to 1
                signal = 1
            # Check if MACD is below signal line
            elif row['macd'] < row['macd_signal']:
                # Set signal to -1
                signal = -1
        # Branch based upon signal value
        if signal == 1:
            # Set order type to buy
            order_type = "BUY_STOP"
            # Set stop price to high of previous candle
            stop_price = dataframe.loc[index - 1, 'high'] # <- Change this to change your stop price
            # Set stop loss to low of previous candle
            stop_loss = dataframe.loc[index - 1, 'low'] # <- Change this to change your stop loss
            # Set take profit to the distance between the stop price and stop loss added to stop price
            distance = stop_price - stop_loss # <- Change this to change your take profit distance
            take_profit = stop_price + distance
        elif signal == -1:
            # Set order type to sell
            order_type = "SELL_STOP"
            # Set stop price to low of previous candle
            stop_price = dataframe.loc[index - 1, 'low'] # <- Change this to change your stop price
            # Set stop loss to high of previous candle
            stop_loss = dataframe.loc[index - 1, 'high'] # <- Change this to change your stop loss
            # Set take profit to the distance between the stop price and stop loss added to stop price
            distance = stop_loss - stop_price # <- Change this to change your take profit distance
            take_profit = stop_price - distance
        else:
            # Set order type to None
            order_type = None
            # Set stop price to 0
            stop_price = 0
            # Set stop loss to 0
            stop_loss = 0
            # Set take profit to 0
            take_profit = 0
        # Set values in dataframe
        dataframe.loc[index, 'order_type'] = order_type
        dataframe.loc[index, 'stop_price'] = stop_price
        dataframe.loc[index, 'stop_loss'] = stop_loss
        dataframe.loc[index, 'take_profit'] = take_profit
    # Return dataframe
    return dataframe
