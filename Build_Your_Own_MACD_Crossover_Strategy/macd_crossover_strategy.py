
import mt5_lib
import indicator_lib


# Main MACD Crossover Strategy Function
def macd_crossover_strategy(symbol, timeframe, macd_fast=12, macd_slow=26, macd_signal=9, exchange="mt5"):
    """
    Main MACD Crossover Strategy Function
    :param symbol: string. Symbol to be analyzed
    :param timeframe: string. Timeframe to be analyzed
    :param macd_fast: integer. Fast EMA Size, default 12.
    :param macd_slow: integer. Slow EMA Size, default 26.
    :param macd_signal: integer. Signal EMA size.
    :param exchange: string. Exchange being traded.
    :return: trade signal dataframe
    """
    ### Pseudo Code ###
    # 1. Retrieve data => get_data()
    # 2. Calculate indicators => calc_indicators()
    # 3. Calculate trade signals => calc_signals()

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
    # Step 3: Calculate signals from indicators
    data = calc_signal(
        dataframe=data
    )
    # Step 4 (not covered in this episode): AutoTrade MACD Crossover Strategy
    # Return signals
    return data

# Function to retrieve data for strategy
def get_data(symbol, timeframe, exchange="mt5"):
    """
    Function to retrieve data from specified exchange. Data is in the form of candlesticks (OHLC) and should be in a
    dataframe format.
    :param symbol: string of the symbol to retrieve
    :param timeframe: string of the timeframe to retrieve
    :param exchange: string of the exchange to retrieve
    :return: dataframe
    """
    if exchange == "mt5":
        # Retrieve data from MT5
        data = mt5_lib.get_candlesticks(
            symbol=symbol,
            timeframe=timeframe,
            number_of_candles=1000
        )
    # Add other exchanges here as needed
    # If exchange not covered, raise error
    else:
        raise ValueError("Exchange not supported yet. Contact james@creativeappnologies.com for assistance")
    # Return data to the user
    return data


# Function to calculate the indicators for the MACD Crossover Strategy
def calc_indicators(dataframe, macd_fast=12, macd_slow=26, macd_signal=9):
    """
    Function to calculate the indicators for the MACD Crossover Strategy.
    :param dataframe: dataframe of the data to be analyzed
    :param macd_fast: integer of the Fast EMA Size.
    :param macd_slow: integer of the Slow EMA Size.
    :param macd_signal: integer of the Signal EMA Size.
    :return: dataframe with indicators
    """
    # Calculate the MACD Indicator
    dataframe = indicator_lib.calc_macd(
        dataframe=dataframe,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )
    # Calculate the MACD Crossover Indicator
    dataframe = indicator_lib.calc_crossover(
        dataframe=dataframe,
        column_one="macd",
        column_two="macd_signal"
    )
    # Return dataframe
    return dataframe


# Function to calculate the signal for the MACD Strategy
def calc_signal(dataframe):
    """
    Function to calculate the signals for the MACD Crossover Strategy. Values can be modified as needed.
    :param dataframe: dataframe containing all the indicator information
    :return: dataframe with trade signals
    """
    # Add columns for order_type, stop_price, stop_loss, and take_profit
    dataframe['order_type'] = ""
    dataframe['stop_price'] = 0
    dataframe['stop_loss'] = 0
    dataframe['take_profit'] = 0
    # Iterate through the dataframe. If 'crossover' column is True, determine the direction of the cross then calculate
    # the signal
    # Get the initial index value
    start_index = dataframe.index[0]
    for index, row in dataframe.iterrows():
        # Skip the first
        # Set the signal variable
        signal = 0
        # Check for a crossover
        if row['crossover']:
            # Check of MACD is above signal line
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
                # Set order type to BUY
                order_type = "BUY_STOP"
                # Set stop price to high or previous candle
                stop_price = dataframe.loc[index-1, 'high'] # <- change this line if you want a different stop price
                # Set stop loss to low of previous candle
                stop_loss = dataframe.loc[index-1, 'low'] # <- change this line to change stop loss value
                # Set take profit to distance between the stop price and stop loss (i.e. 1:1)
                distance = stop_price - stop_loss # <- Change this line to change the Take Profit ratio
                take_profit = stop_price + distance
            elif signal == -1:
                # Set order type to SELL_STOP
                order_type = "SELL_STOP"
                # Set stop price to low of previous candle
                stop_price = dataframe.loc[index - 1, 'low'] # <- Change this line to change stop price
                # Set stop loss to high of previous candle
                stop_loss = dataframe.loc[index - 1, 'high'] # <- Change this to change your stop loss
                # Set the take profit to the distance between the stop price and stop loss added to the stop price
                # (i.e. 1:1)
                distance = stop_loss - stop_price # <- Change this line to change your profit ratio
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

            # Update the values in the dataframe
            dataframe.loc[index, 'order_type'] = order_type
            dataframe.loc[index, 'stop_price'] = stop_price
            dataframe.loc[index, 'stop_loss'] = stop_loss
            dataframe.loc[index, 'take_profit'] = take_profit

    # Return dataframe
    return dataframe