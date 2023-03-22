import json
import os

import pandas

import time

import backtest_lib
import indicator_lib
import mt5_lib
from strategies import macd_crossover_strategy

# Location of settings.json
settings_filepath = "../tutorial/settings.json" # <- This can be modified to be your own settings filepath


# Function to import settings from settings.json
def get_project_settings(import_filepath):
    """
    Function to import settings from settings.json
    :param import_filepath: path to settings.json
    :return: settings as a dictionary object
    """
    # Test the filepath to make sure it exists
    if os.path.exists(import_filepath):
        # If yes, import the file
        f = open(import_filepath, "r")
        # Read the information
        project_settings = json.load(f)
        # Close the file
        f.close()
        # Return the project settings
        return project_settings
    # Notify user if settings.json doesn't exist
    else:
        raise ImportError("settings.json does not exist at provided location")


# Function to start up MT5
def mt5_startup(project_settings):
    """
    Function to run through the process of starting up MT5 and initializing symbols
    :param project_settings: json object of project settings
    :return: Boolean. True. Startup successful. False. Error in starting up.
    """
    # Attempt to start MT5
    start_up = mt5_lib.start_mt5(project_settings=project_settings)
    # If starting up successful, proceed to confirm that the symbols are initialized
    if start_up:
        init_symbols = mt5_lib.enable_all_symbols(symbol_array=project_settings["mt5"]["symbols"])
        if init_symbols:
            return True
        else:
            print(f"Error intializing symbols")
            return False
    else:
        print(f"Error starting MT5")
        return False


# Main function
if __name__ == '__main__':
    print("Let's build an awesome trading bot!!!")
    # Import settings.json
    project_settings = get_project_settings(import_filepath=settings_filepath)
    # Start MT5
    mt5_start = mt5_startup(project_settings=project_settings)
    pandas.set_option('display.max_columns', None)
    comment = "ema_cross_strategy"
    # Start a Performance timer
    perf_start = time.perf_counter()
    # If MT5 starts correctly, lets query for some candles
    if mt5_start:
        # Backtest values
        symbol = "ETHUSD"
        timeframe = "D1"
        time_to_test = "1Year"
        # Calculate the MACD Crossover Strategy
        data = macd_crossover_strategy.macd_crossover_strategy(
            symbol=symbol,
            timeframe=timeframe,
            time_to_test=time_to_test,
            time_to_cancel="num_minutes=60"
        )
        # Fire off the forex backtest
        backtest_results = backtest_lib.forex_backtest(
            strategy_dataframe=data,
            cash=100000,
            commission=0.002,
            symbol=symbol,
            exchange="mt5",
            time_to_test=time_to_test,
            risk_percent=0.01,
            candle_timeframe=timeframe
        )
    perf_stop = time.perf_counter()
    print(f"Total time to run: {perf_stop - perf_start}")



