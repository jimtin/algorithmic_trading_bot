import json
import os

import pandas

import time

import display_lib
import indicator_lib
import mt5_lib
import macd_crossover_strategy
import ema_cross_strategy
import make_trade
import backtest_lib

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
        strat = macd_crossover_strategy.macd_crossover_strategy(
            symbol="ETHUSD.a",
            timeframe="H1",
            exchange="mt5",
        )
        print(strat)
        # Extract only true crossover signals
        cross_events = strat[strat["crossover"] == True]
        print(cross_events)
        # Set the parameters

