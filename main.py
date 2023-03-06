import json
import os

import pandas

import time
import mt5_lib
import ema_cross_strategy
import make_trade

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
    # If MT5 starts correctly, lets query for some candles
    if mt5_start:
        # Set a variable for current time
        current_time = 0
        # Set a variable for previous time
        previous_time = 0
        while 1:
            # Get the last candle for any trading pair
            candle = mt5_lib.query_historic_data("USDJPY.a", "M30", 1)
            current_time = candle['time'][0]
            if current_time != previous_time:
                print("New Candle")
                previous_time = current_time
                # Iterate through the symbols
                for symbol in project_settings['mt5']['symbols']:
                    # Cancel any current open orders
                    orders = mt5_lib.get_filtered_list_of_orders(
                        symbol=symbol,
                        comment=comment
                    )
                    if len(orders) > 0:
                        for order in orders:
                            mt5_lib.cancel_order(order)
                    # Extract the timeframe
                    timeframe = project_settings['mt5']['timeframe']
                    # Pass into the strategy function
                    strategy = ema_cross_strategy.ema_cross_strategy(
                        symbol=symbol,
                        timeframe=timeframe,
                        ema_one=50,
                        ema_two=200
                    )
                    # If the last row of the strategy ema_cross is True, make a trade
                    trade = strategy.iloc[-1]['ema_cross']
                    if trade:
                        # Extract the values needed
                        balance = 10000.00 #<- Change this to a different value or subscribe to see how to update it dynamically
                        risk = 0.01 #<- Risk 1% of capital each time
                        take_profit = strategy.iloc[-1]['take_profit']
                        stop_price = strategy.iloc[-1]['stop_price']
                        stop_loss = strategy.iloc[-1]['stop_loss']

                        # Send to MT5
                        trade_outcome = make_trade.make_trade(
                            balance=balance,
                            amount_to_risk=risk,
                            symbol=symbol,
                            take_profit=take_profit,
                            stop_loss=stop_loss,
                            stop_price=stop_price
                        )
                        print(f"Make a Trade! Outcome: {trade_outcome}")
                    else:
                        print("No Trade")
            else:
                time.sleep(1)
