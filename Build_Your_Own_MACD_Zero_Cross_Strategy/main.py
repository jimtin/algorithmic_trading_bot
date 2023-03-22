import json
import os
import time

import pandas

# Custom Libraries
import mt5_lib
import macd_zero_cross_strategy

# Location of settings.json
settings_filepath = "settings.json" # <- This can be modified to be your own settings filepath


# Function to import settings from settings.json
def get_project_settings(import_filepath):
    """
    Function to import settings from settings.json.
    Documentation:
    - YouTube - https://youtu.be/jpw3JltNMg0
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


# Function to repeat startup proceedures
def start_up(project_settings):
    """
    Function to manage start up proceedures for App. Includes starting/testing exchanges
    initializing symbols and anything else to ensure app start is successful.
    Documentation:
    - YouTube: https://youtu.be/EkP7iAZoMEw
    :param project_settings: json object of the project settings
    :return: Boolean. True if app start up is successful. False if not.
    """
    # Start MetaTrader 5
    startup = mt5_lib.start_mt5(project_settings=project_settings)
    # If startup successful, let user know
    if startup:
        print("MetaTrader startup successful")
        # Initialize symbols
        # Extract symbols from project settings
        symbols = project_settings["mt5"]["symbols"]
        # Iterate through the symbols to enable
        for symbol in symbols:
            outcome = mt5_lib.initialize_symbol(symbol)
            # Update the user
            if outcome is True:
                # print(f"Symbol {symbol} initalized")
                pass
            else:
                raise Exception(f"{symbol} not initialized")
        return True
    # Default return is False
    return False


# Function to run the strategy
def run_strategy(project_settings):
    """
    Function to run the strategy for the trading bot.
    Documentation:
    - 3 Part YouTube series: https://youtu.be/ecK0ZbMWVIA , https://youtu.be/Q5GQFxk1IJI , https://youtu.be/4NDO81n-EpA
    :param project_settings: JSON of project settings
    :return: Boolean. Strategy ran successfully with no errors=True. Else False.
    """
    # Extract the symbols to be traded
    symbols = project_settings["mt5"]["symbols"]
    # Extract the timeframe to be traded
    timeframe = project_settings["mt5"]["timeframe"]
    # Strategy Risk Management
    # Get a list of open orders
    orders = mt5_lib.get_all_open_orders()
    # Iterate through the open orders and cancel
    for order in orders:
        mt5_lib.cancel_order(order)
    # Run through the strategy of the specified symbols
    for symbol in symbols:
        # Strategy Risk Management
        # Generate the comment string
        comment_string = f"EMA_Cross_strategy_{symbol}"
        # Cancel any open orders related to the symbol and strategy
        mt5_lib.cancel_filtered_orders(
            symbol=symbol,
            comment=comment_string
        )
        # Trade Strategy
        data = ema_cross_strategy.ema_cross_strategy(
            symbol=symbol,
            timeframe=timeframe,
            ema_one=50,
            ema_two=200,
            balance=10000,
            amount_to_risk=0.01
        )
        if data:
            print(f"Trade Made on {symbol}")
        else:
            print(f"No trade for {symbol}")
    # Return True. Previous code will throw a breaking error if anything goes wrong.
    return True


# Main function
if __name__ == '__main__':
    print("Let's build an awesome trading bot!!!")
    # Import settings.json
    project_settings = get_project_settings(import_filepath=settings_filepath)
    # Run through startup proceedure
    startup = start_up(project_settings=project_settings)
    # Make it so that all columns are shown
    pandas.set_option('display.max_columns', None)
    # If Startup successful, start trading while loop
    if startup:
        # Get strategy data
        strategy = macd_zero_cross_strategy.macd_zero_cross_strategy(
            symbol="ETHUSD",
            timeframe="H1",
        )
        print(strategy)
        # Extract only rows which have a trade
        trade_values = strategy[strategy['zero_cross'] == True]
        print(trade_values)



