import json
import os

import pandas

import time

import backtest_lib
import display_lib
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
        """
        # Get the data
        data = mt5_lib.get_candlesticks(
            symbol="ETHUSD.a",
            timeframe="H6",
            number_of_candles=1000,
        )
        # Create the indicators
        rsi = indicator_lib.calc_rsi(dataframe=data, rsi_size=14, display=True, symbol="ETHUSD.a")
        display_lib.display_graph(rsi, "ETHUSD Price Chart", dash=True)
        """
        # Backtest values
        symbols = ["ETHUSD.a"]
        timeframes = ["H6"]
        time_to_test = "1Year"
        # Set the params
        # MACD Params: take_profit, stop_loss, fast_ema, slow_ema, signal_ema, time_to_cancel
        strategy_params = [
            [1], [1], list(range(5, 6)), [26], [9], [16]
        ]
        # Backets
        backtest_results = backtest_lib.forex_backtest(
            strategy="MACD_Crossover",
            cash=10000,
            commission=0.002,
            symbols=symbols,
            timeframes=timeframes,
            risk_percent=0.01,
            exchange="mt5",
            time_to_test=time_to_test,
            strategy_params=strategy_params,
            optimize_params=True,
            optimize_stop_loss=False,
            optimize_take_profit=False,
            optimize_order_cancel_time=False,
            display_results=True,
            trailing_stop_pips=900,
            trailing_take_profit_pips=900
        )
        # Convert the backtest results to a dataframe
        backtest_results = pandas.DataFrame(backtest_results)
        # Output the results to JSON
        backtest_results.to_json(f"backtest_results_{comment}.json")

    perf_stop = time.perf_counter()
    print(f"Total time to run: {perf_stop - perf_start}")



