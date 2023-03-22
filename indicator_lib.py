import pandas
import numpy as np
import talib
import display_lib


# Define a function to calculate an EMA of any size
def calc_ema(dataframe, ema_size):
    """
    Function to calculate a dataframe of any size. Does not use TA-Lib, so slows down for dataframes greater
    than about 5000 (depending on computer architecture)
    :param dataframe: dataframe of raw candlestick sizes
    :param ema_size: integer of the size of EMA you want
    :return: dataframe with EMA attached
    """
    # Create the name of the column to be added
    ema_name = "ema_" + str(ema_size)
    # Create the multiplier
    multiplier = 2/(ema_size + 1)
    # Calculate the initial value. This will be a Simple Moving Average (SMA)
    initial_mean = dataframe['close'].head(ema_size).mean()
    # Iterate through the dataframe and add the values
    for i in range(len(dataframe)):
        # If i is the size of the EMA, this value will be the initial mean
        if i == ema_size:
            dataframe.loc[i, ema_name] = initial_mean
        # If i is > ema_size, calculate the EMA
        elif i > ema_size:
            ema_value = dataframe.loc[i, 'close'] * multiplier + dataframe.loc[i-1, ema_name]*(1-multiplier)
            dataframe.loc[i, ema_name] = ema_value
        # If i is < ema_size, set value to be 0.00
        else:
            dataframe.loc[i, ema_name] = 0.00
    # Return completed dataframe to the user
    return dataframe

# Function to calculate an EMA cross event
def calc_ema_cross(dataframe, ema_one, ema_two):
    """
    Function to calculate an EMA cross event. EMA Column names must be in the format ema_<value>. I.e. an EMA 200
    would be ema_200
    :param dataframe: Panda's Dataframe object
    :param ema_one: integer of EMA 1
    :param ema_two: integer of EMA 2
    :return: dataframe with cross events
    """
    # Get ema_one column name
    ema_one_column = "ema_" + str(ema_one)
    # Get ema_two column name
    ema_two_column = "ema_" + str(ema_two)
    # Create a position column
    dataframe['position'] = dataframe[ema_one_column] > dataframe[ema_two_column]
    # Create a pre-position column which is the previous row shifted by 1
    dataframe['pre_position'] = dataframe['position'].shift(1)
    # Drop any NA values
    dataframe.dropna(inplace=True)
    # Define Crossover events
    dataframe['ema_cross'] = np.where(dataframe['position'] == dataframe['pre_position'], False, True)
    # Remove the 'position' column
    dataframe = dataframe.drop(columns='position')
    # Remove the 'pre_position' column
    dataframe = dataframe.drop(columns='pre_position')
    # Return dataframe
    return dataframe


# Function to calculate a generic crossover event
def calc_crossover(dataframe, column_one, column_two):
    """
    Function to calculate a generic crossover event
    :param dataframe: Panda's Dataframe object
    :param column_one: string of the column name of the first column
    :param column_two: string of the column name of the second column
    :return: dataframe with cross events
    """
    # Create a position column
    dataframe['position'] = dataframe[column_one] > dataframe[column_two]
    # Create a pre-position column which is the previous row shifted by 1
    dataframe['pre_position'] = dataframe['position'].shift(1)
    # Drop any NA values
    dataframe.dropna(inplace=True)
    # Define Crossover events
    dataframe['crossover'] = np.where(dataframe['position'] == dataframe['pre_position'], False, True)
    # Remove the 'position' column
    dataframe = dataframe.drop(columns='position')
    # Remove the 'pre_position' column
    dataframe = dataframe.drop(columns='pre_position')
    # Return dataframe
    return dataframe


# Function to calculate a zero cross event
def calc_zero_cross(dataframe, column):
    """
    Function to calculate a zero cross event
    :param dataframe: Panda's Dataframe object
    :param column: string of the column name of the column to be checked
    :return: dataframe with cross events
    """
    # Create a position column
    dataframe['position'] = dataframe[column] > 0
    # Create a pre-position column which is the previous row shifted by 1
    dataframe['pre_position'] = dataframe['position'].shift(1)
    # Drop any NA values
    dataframe.dropna(inplace=True)
    # Define Crossover events
    dataframe['zero_cross'] = np.where(dataframe['position'] == dataframe['pre_position'], False, True)
    # Remove the 'position' column
    dataframe = dataframe.drop(columns='position')
    # Remove the 'pre_position' column
    dataframe = dataframe.drop(columns='pre_position')
    # Return dataframe
    return dataframe


# Function to calculate EMA using ta-lib
def calc_ema_ta(dataframe, ema_size, display=False, symbol=None, fig=None):
    """
    Function to calculate an EMA using the TA-Lib library
    :param dataframe: dataframe of the raw candlestick data
    :param ema_size: integer of the size of EMA you want
    :return: dataframe with EMA attached
    """
    # Create the name of the column to be added
    ema_name = "ema_" + str(ema_size)
    # Calculate the EMA
    dataframe[ema_name] = talib.EMA(dataframe['close'], timeperiod=ema_size)
    if display:
        title = symbol + " EMA " + str(ema_size) + " Indicator"
        fig = display_lib.add_line_to_graph(
            base_fig=fig,
            dataframe=dataframe,
            dataframe_column=ema_name,
            line_name=title
        )
        # Return the figure
        return fig
    else:
        # If not displaying, return the dataframe
        return dataframe


# Function to calculate a MACD Indicator
def calc_macd(dataframe, macd_fast=12, macd_slow=26, macd_signal=9, display=False, symbol=None):
    """
    Function to calculate a MACD indicator
    :param dataframe: dataframe of the raw candlestick data
    :param macd_fast: integer of the fast EMA size
    :param macd_slow: integer of the slow EMA size
    :param macd_signal: integer of the signal EMA size
    :param display: boolean to determine whether the MACD indicator should be displayed
    :param symbol: string of the symbol to be displayed on the graph
    :return: dataframe with MACD values included
    """
    # Calculate the MACD values in the dataframe
    dataframe['macd'], dataframe['macd_signal'], dataframe['macd_histogram'] = talib.MACD(
        dataframe['close'],
        fastperiod=macd_fast,
        slowperiod=macd_slow,
        signalperiod=macd_signal
    )
    if display:
        title = symbol + " MACD Indicator"
        fig = display_lib.display_macd_indicator(
            dataframe=dataframe,
            title=title
        )
        # Return the dataframe
        return fig
    else:
        # If not displaying, return the dataframe
        return dataframe


# Function to calculate the RSI indicator
def calc_rsi(dataframe, rsi_size=14, display=False, symbol=None):
    """
    Function to calculate the RSI indicator. Default period is 14.
    :param dataframe: dataframe object of security to have RSI applied to
    :param rsi_size: size of the RSI oscillation. Default 14.
    :param display: boolean to determine whether the RSI indicator should be displayed
    :param symbol: string. Used for display
    :return: dataframe with RSI values included or figure
    """
    # Calculate the RSI values in the dataframe
    dataframe['rsi'] = talib.RSI(dataframe['close'], timeperiod=rsi_size)
    if display:
        title = symbol + " RSI Indicator"
        fig = display_lib.display_rsi_indicator(
            dataframe=dataframe,
            title=title
        )
        # Return the dataframe
        return fig
    else:
        # If not displaying, return the dataframe
        return dataframe