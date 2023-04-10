# Part of article: Make Your Own MACD Crossover Strategy with MetaTrader 5 and Python
# Link: https://medium.com/@appnologyjames/build-the-macd-crossover-strategy-with-your-metatrader-5-python-trading-bot-98daa630261
# Part of Algorithmic Trading Bot: https://github.com/jimtin/algorithmic_trading_bot


import mt5_lib
import indicator_lib
import pandas


# Main MACD Crossover Strategy Function
def macd_crossover_strategy(time_to_test, time_to_cancel, macd_fast=12, macd_slow=26, macd_signal=9, exchange="mt5",
                            symbol="", timeframe="", dataframe=None, stop_loss_multiplier=1, take_profit_multiplier=1):
    """
    Main MACD Crossover Strategy Function
    :param symbol: symbol to be analyzed
    :param timeframe: timeframe to analyze
    :param time_to_test: time to test strategy over. Accepted values: "1Month", "3Months", "6Months", "1Year", "2Years", "3Years", "5Years", "All"
    :param time_to_cancel: time to cancel orders on dataframe. Accepted values: "Candle", "GTC", "OCO", "num_minutes=<val>"
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

    # raise an error if the dataframe is None, and symbol or timeframe are empty
    if dataframe is None and (symbol == "" or timeframe == ""):
        raise ValueError("No data to analyze")
    # Pass if the fast EMA is larger than the slow EMA
    if macd_fast > macd_slow:
        return False

    # Step 1: Retrieve data
    if dataframe is None:
        # Check that the time to test is valid
        if time_to_test not in ["1Month", "3Months", "6Months", "1Year", "2Years", "3Years", "5Years", "All"]:
            raise ValueError("Chosen time_to_test range not supported")
        data = get_data(
            symbol=symbol,
            timeframe=timeframe,
            exchange=exchange,
            time_to_test=time_to_test
        )
    else:
        data = dataframe
    # Step 2: Pass data to calculate indicators
    # Return False if the dataframe is empty
    if len(data) == 0:
        return False
    data = calc_indicators(
        dataframe=data,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )
    # If data is False, return False
    if data is False:
        return False
    # Step 3: Calculate trade events
    data = calc_signal(
        dataframe=data,
        take_profit_multiplier=take_profit_multiplier,
        stop_loss_multiplier=stop_loss_multiplier
    )
    if data is False:
        return False
    # If Time to Cancel set to the next candle, shift the dataframe
    if time_to_cancel == "Candle":
        # Update the dataframe with the human_time from the next column
        data["cancel_time"] = data["human_time"].shift(-1)
    # Extract only the true values from the dataframe
    data = data[data["crossover"] == True]
    # Step 4: Update Dataframe with a column for trade cancellation
    if time_to_cancel == "GTC":
        # Update the dataframe with a value of "GTC"
        data["cancel_time"] = "GTC"
    elif time_to_cancel == "OCO":
        # Set the cancel_time to the human_time from the next row
        data["cancel_time"] = data["human_time"].shift(-1)
    else:
        # Convert to integer
        time_to_cancel = int(time_to_cancel)
        # Add this to the 'human_time' column of the dataframe to get the cancel time
        data["cancel_time"] = data["human_time"] + pandas.Timedelta(minutes=time_to_cancel)
    # Return outcome to user
    return data


# Function to retrieve data for strategy
def get_data(symbol, timeframe, time_to_test, exchange="mt5"):
    """
    Function to retrieve data from MT5. Data is in the form of candlesticks and should be returned as a
    dataframe
    :param symbol: string of the symbol to be retrieved
    :param timeframe: string of the timeframe to be queried
    :return: dataframe
    """
    if exchange == "mt5":
        # Note, this function can be expanded to retrieve data from other exchanges also.
        data = mt5_lib.query_historic_data_by_time(
            symbol=symbol,
            timeframe=timeframe,
            time_range=time_to_test
        )
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
def calc_signal(dataframe, take_profit_multiplier=1, stop_loss_multiplier=1):
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
    if len(dataframe) == 0:
        return False
    # Get the initial index value
    start_index = dataframe.index[0]
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
        # Skip the first row
        if index > start_index:
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
                # Multiply stop loss by stop loss multiplier
                stop_loss = stop_loss * stop_loss_multiplier
                # Multiply take profit by take profit multiplier
                take_profit = take_profit * take_profit_multiplier
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
                # Multiply stop loss by stop loss multiplier
                stop_loss = stop_loss * stop_loss_multiplier
                # Multiply take profit by take profit multiplier
                take_profit = take_profit * take_profit_multiplier
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
