# Part of article: Build Your Own MACD Zero Cross Strategy Using MetaTrader and Python
# Link: https://medium.com/@appnologyjames/build-your-own-macd-zero-cross-strategy-using-metatrader-and-python-ba1c67b0d8ba
# Part of Algorithmic Trading Bot: https://github.com/jimtin/algorithmic_trading_bot


import indicator_lib # <- Import your indicator library
import helper_functions


# Function to define the MACD Zero Cross Strategy
def macd_zero_cross_strategy(symbol, timeframe, macd_fast=12, macd_slow=26, macd_signal=9, exchange="mt5"):
    """
    Function to define the MACD Zero Cross Strategy
    :param symbol: string of the symbol to be retrieved
    :param timeframe: string of the timeframe to be queried
    :param macd_fast: fast EMA size
    :param macd_slow: slow EMA size
    :param macd_signal: signal EMA size
    :param exchange: string of the exchange to be queried
    :return: dataframe with trade signals
    """
    # Retrieve data
    data = helper_functions.get_data(
        symbol=symbol,
        timeframe=timeframe,
        exchange=exchange
    )
    # Calculate indicators
    data = calc_indicators(
        dataframe=data,
        macd_fast=macd_fast,
        macd_slow=macd_slow,
        macd_signal=macd_signal
    )
    # Calculate trade signals
    data = calc_signal(
        dataframe=data
    )
    # Return outcome to user
    return data


# Function to calculate indicators for the strategy
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
    # Calculate MACD Zero Cross Indicator
    dataframe = indicator_lib.calc_zero_cross(
        dataframe=dataframe,
        column="macd"
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
    # Add columns for order_type, stop_price, stop_loss, and take_profit
    dataframe["order_type"] = ""
    dataframe["stop_price"] = 0.0
    dataframe["stop_loss"] = 0.0
    dataframe["take_profit"] = 0.0
    # Drop the first row as this will always be true, but will lack the previous row to calculate the stop price
    dataframe = dataframe.drop(dataframe.index[0])
    # Iterate through the dataframe. If 'zero_cross' column is true, determine if the MACD is above or below zero.
    for index, row in dataframe.iterrows():
        if row["zero_cross"]:
            if row["macd"] < 0:
                order_type = "SELL_STOP"
                stop_price = dataframe.loc[index-1, "low"]
                stop_loss = dataframe.loc[index-1, "high"]
                distance = stop_loss - stop_price
                take_profit = stop_loss - distance
            else:
                order_type = "BUY_STOP"
                stop_price = dataframe.loc[index-1, "high"]
                stop_loss = dataframe.loc[index-1, "low"]
                distance = stop_price - stop_loss
                take_profit = stop_loss + distance
            # Update the dataframe with values
            dataframe.at[index, "order_type"] = order_type
            dataframe.at[index, "stop_price"] = stop_price
            dataframe.at[index, "stop_loss"] = stop_loss
            dataframe.at[index, "take_profit"] = take_profit
        else:
            dataframe.at[index, "order_type"] = ""
    # Return dataframe
    return dataframe
