import numpy as np
import talib


# Define a function to calculate a custom EMA of any size
def calc_custom_ema(dataframe, ema_size):
    """
    Function to calculate a dataframe of any size. Does not use TA-Lib, so is a custom implementation.
    Recommended to keep dataframe size < 1000 rows to preserve speed.
    :param dataframe: dataframe object of the price data to apply ema to
    :param ema_size: integer of the size of EMA
    :return: dataframe with EMA attached
    """
    # Create the name of the column to be added
    ema_name = "ema_" + str(ema_size)
    # Create the multiplier
    multiplier = 2 / (ema_size + 1)
    # Calculate the initial value. This will be a Simple Moving Average
    initial_mean = dataframe['close'].head(ema_size).mean()
    # Iterate through the dataframe and add the values
    for i in range(len(dataframe)):
        # If i is the size of the EMA, value is the initial mean
        if i == ema_size:
            dataframe.loc[i, ema_name] = initial_mean
        # If i is > ema_size, calculate the EMA
        elif i > ema_size:
            ema_value = dataframe.loc[i, 'close'] * multiplier + dataframe.loc[i-1, ema_name]*(1-multiplier)
            dataframe.loc[i, ema_name] = ema_value
        # If i is < ema_size (also the default condition)
        else:
            dataframe.loc[i, ema_name] = 0.00

    # Once completed, return the completed dataframe to the user
    return dataframe


# Function to calculate a crossover event between two EMAs
def ema_cross_calculator(dataframe, ema_one, ema_two):
    """
    Function to calculate an EMA cross event. EMA Column names must be in the format ema_<value>. I.e. an EMA 200
    would be ema_200
    :param dataframe: dataframe object
    :param ema_one: integer of EMA 1 size
    :param ema_two: integer of EMA 2 size
    :return: dataframe with cross events
    """
    # Get the column names
    ema_one_column = "ema_" + str(ema_one)
    ema_two_column = "ema_" + str(ema_two)
    # Create a position column
    dataframe['position'] = dataframe[ema_one_column] > dataframe[ema_two_column]
    # Create a pre-position column
    dataframe['pre_position'] = dataframe['position'].shift(1)
    # Drop any NA values
    dataframe.dropna(inplace=True)
    # Define the Crossover events
    dataframe['ema_cross'] = np.where(dataframe['position'] == dataframe['pre_position'], False, True)
    # Drop the position and pre_position columns
    dataframe = dataframe.drop(columns="position")
    dataframe = dataframe.drop(columns="pre_position")
    # Return dataframe
    return dataframe


# Function to calculate a Moving Average Convergence / Divergence Indicator
def calc_macd(dataframe, macd_fast=12, macd_slow=26, macd_signal=9):
    """
    Function to calculate a MACD Indicator. Uses default values for input EMA's, which can be modified as needed.
    Documentation:
    - Medium:
        - https://medium.com/@appnologyjames/macd-indicator-explained-with-examples-strategies-limitations-and-a-little-bit-of-code-38d0188f80b9
        - https://medium.com/@appnologyjames/how-to-add-the-macd-indicator-to-your-metatrader-5-python-trading-bot-1443845c41e4
    :param dataframe: dataframe of the raw candlestick data. Must include a 'close' column
    :param macd_fast: integer of the smaller EMA. Default 12.
    :param macd_slow: integer of the larger EMA. Default 26.
    :param macd_signal: integer of the EMA of the MACD Lin. Default 9.
    :return: dataframe with MACD Line, MACD Signal Line, and Histogram values.
    """
    # Calculate the MACD values in the dataframe
    dataframe['macd'], dataframe['macd_signal'], dataframe['macd_histogram'] = talib.MACD(
        dataframe['close'],
        fastperiod=macd_fast,
        slowperiod=macd_slow,
        signalperiod=macd_signal
    )
    # Return the dataframe to the function
    return dataframe


# Calculate a crossover event in a dataframe
def calc_crossover(dataframe, column_one, column_two):
    """
    Function to calculate a generic crossover event
    :param dataframe: dataframe object
    :param column_one: string of the name of the first column
    :param column_two: string of the name of the second column
    :return: dataframe with cross events identified
    """
    # Create a position column
    dataframe['position'] = dataframe[column_one] > dataframe[column_two]
    # Create a pre-position column which is the previous row shifted by 1
    dataframe['pre_position'] = dataframe['position'].shift(1)
    # Drop any NA values
    dataframe.dropna(inplace=True)
    # Define crossover events
    dataframe['crossover'] = np.where(dataframe['position'] == dataframe['pre_position'], False, True)
    # Remove the 'position' column
    dataframe = dataframe.drop(columns='position')
    # Remove the 'pre_position' column
    dataframe = dataframe.drop(columns='pre_position')
    # Return the completed dataframe
    return dataframe
