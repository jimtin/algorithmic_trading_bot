import multiprocessing

from backtesting import Strategy, Backtest
from backtesting.lib import crossover

import display_lib
import indicator_lib
import talib
import mt5_lib
import pandas
import os
import helper_functions
from backtesting_py_strategies import ema_cross


# Function to multi-optimize a strategy
def multi_optimize(strategy, cash, commission, symbols, timeframes, exchange, time_to_test, params={}, forex=False,
                   risk_percent=None):
    """
    Function to run a backtest optimizing across symbols, timeframes
    :param strategy: string of the strategy to be tested
    :param cash: integer of the cash to start with
    :param commission: decimal value of the percentage commission fees
    :param symbols: string of the symbol to be tested
    :param timeframes: string of the timeframe to be tested
    :param exchange: string identifying the exchange to retreive data from
    :param time_to_test: string identifying the timeframe to test. Options are: 1Month, 3Months, 6Months, 1Year, 2Years,
    3Years, 5Years, All
    :param params: dictionary of parameters to be optimized
    :return:
    """
    # Todo: Add in support for using custom indicators
    # Check the time_to_test variable for approved values
    if time_to_test not in ["1Month", "3Months", "6Months", "1Year", "2Years", "3Years", "5Years", "All"]:
        raise ValueError("Chosen time_to_test range not supported")
    # Instantiate an empty list to store results
    results_list = []
    # Create a list of arguments to pass to the run_backtest function
    args_list = []
    # Iterate through the symbols
    for symbol in symbols:
        # Iterate through the timeframes
        for timeframe in timeframes:
            # Get data from exchange. Keep this single threaded
            if exchange == "mt5":
                data = mt5_lib.query_historic_data_by_time(
                    symbol=symbol,
                    timeframe=timeframe,
                    time_range=time_to_test
                )
                # Get current working directory
                save_location = os.path.abspath(os.getcwd())
                # Create the save path
                plot_save_path = f"{save_location}" + "/plots/" + f"{strategy}" + "_" + f"{exchange}" + "_" + \
                                 f"{symbol}" + "_" + f"{timeframe}" + "_" + f"{cash}" + "_" + f"{commission}" + "_" + \
                                 ".html"
                result_save_path = f"{save_location}" + "/results/" + f"{strategy}" + "_" + f"{exchange}" + "_" + \
                                   f"{symbol}" + "_" + f"{timeframe}" + "_" + f"{cash}" + "_" + f"{commission}" + "_" \
                                   + ".json"
                # Create tuple
                args_tuple = (data, strategy, cash, commission, symbol, timeframe, exchange, True, True,
                              plot_save_path, result_save_path, params, forex, risk_percent)
                # Append to args_list
                args_list.append(args_tuple)
            else:
                raise ValueError("Exchange not supported")

    # Set up Async results
    async_results = []
    # Iterate through the data_list and use multiprocessing to run the backtest
    with multiprocessing.Pool(9) as process_pool:
        result = process_pool.starmap(run_backtest, args_list)

    # Return the results dataframe
    return True


def run_backtest(data, strategy, cash, commission, symbol, timeframe, exchange, optimize=False, save=False,
                 plot_save_location=None, result_save_location=None, params={}, forex=False, risk_percent=None):
    """
    Function to run a backtest
    :param data: raw dataframe to use for backtesting
    :param Strategy: Strategy to use for backtesting
    :param cash: Start cash
    :param commission: Commission fees (percentage expressed as decimal)
    :return: backtest outcomes
    """
    print("Processing")
    if forex:
        print(f"Forex testing framework in use")
    else:
        print(f"Stock testing framework in use")
        ### Reformat dataframe to match backtesting.py requirements
        # Create a new column with name Open using open
        data['Open'] = data['open']
        # Create a new column with name Close using close
        data['Close'] = data['close']
        # Create a new column with name High using high
        data['High'] = data['high']
        # Create a new column with name Low using low
        data['Low'] = data['low']
        # Set index to human_time
        data.set_index('human_time', inplace=True)
        # Get the strategy class
        if strategy == "EMACross":
            strategy = ema_cross.EMACross
            # Initialize the backtest
            backtest = Backtest(data, strategy, cash=cash, commission=commission)
            # If optimize is true, optimize the strategy
            if optimize:
                # Optimize the strategy
                stats = backtest.optimize(
                    n1=params['n1'],
                    n2=params['n2'],
                    maximize='Equity Final [$]',
                    constraint=lambda p: p.n1 < p.n2
                )
            else:
                # Run the backtest
                stats = backtest.run(
                    n1=params['n1'],
                    n2=params['n2']
                )
        else:
            raise ValueError("Strategy not supported")
        # If save is true, save the backtest
        if save:
            backtest.plot(filename=plot_save_location, open_browser=False)
        # Update with information about the backtest
        stats['Strategy'] = strategy
        stats['Cash'] = cash
        stats['Commission'] = commission
        stats['Symbol'] = symbol
        stats['Timeframe'] = timeframe
        stats['Exchange'] = exchange
        stats['Forex'] = forex
        stats['Risk_Percent'] = risk_percent
        if save:
            stats.to_json(result_save_location)

        return stats


# Function to backtest a FOREX strategy
def forex_backtest(strategy_dataframe, cash, commission, symbol, candle_timeframe, exchange, time_to_test, risk_percent, trailing_stop_column=None, trailing_stop_pips=None, trailing_stop_percent=None, trailing_take_profit_column=None, trailing_take_profit_pips=None, trailing_take_profit_percent=None):
    """
    Function to run a single backtest pass
    :param strategy: string of the strategy to be tested
    :param cash: integer of the cash to start with
    :param commission: decimal value of the percentage commission fees
    :param symbols: string of the symbol to be tested
    :param timeframes: string of the timeframe to be tested
    :param exchange: string identifying the exchange to retreive data from
    :param time_to_test: string identifying the timeframe to test. Options are: 1Month, 3Months, 6Months, 1Year, 2Years,
    3Years, 5Years, All
    :param params: dictionary of parameters to be optimized
    :return:
    """
    ### Pseudocode ###
    # 1. Get data pricing data from exchange
    # 2. Iterate through the pricing data and apply against the strategy dataframe. Make sure to store every trade.
    # 3. Calculate the results of the backtest
    # 4. Return the results of the backtest
    # 5. Provide option to display results of the backtest
    # 6. Provide option to save results of the backtest

    # Check the time_to_test variable for approved values
    if time_to_test not in ["1Month", "3Months", "6Months", "1Year", "2Years", "3Years", "5Years", "All"]:
        raise ValueError("Chosen time_to_test range not supported")
    # Check the exchange variable for approved values
    if exchange == "mt5":
        print("Retrieving historic data from MetaTrader 5")
        # Get data from exchange. This will always be the 1min timeframe as this is the smallest timeframe.
        historic_data = mt5_lib.query_historic_data_by_time(
            symbol=symbol,
            timeframe="M1",
            time_range=time_to_test
        )
        # Get the raw candlesticks applicable to the strategy
        raw_candidate_candlesticks = mt5_lib.query_historic_data_by_time(
            symbol=symbol,
            timeframe=candle_timeframe,
            time_range=time_to_test
        )
        # Get a pip_size for the symbol if trailing stop is trailing_stop_pips
        if trailing_stop_pips is not None:
            pip_size = mt5_lib.get_pip_size(symbol)
    else:
        raise ValueError("Chosen exchange not supported")
    # Convert historic_data from a dataframe to a dictionary
    historic_data_dict = historic_data.to_dict('records')
    # Convert the strategy dataframe to a dictionary
    strategy_dataframe_dict = strategy_dataframe.to_dict('records')
    # Create an empty list to store the trades
    trades = []
    # Create an empty list to store completed trades
    completed_trades = []
    # Create a variable to store the current balance
    current_balance = cash
    # Iterate through historic_data_dict and test each row against the strategy
    for strategy_row in strategy_dataframe_dict:
        #print(f"Next Row: {strategy_row}")
        for historic_row in historic_data_dict:
            # Step 1: Check the trades list to see if any trades have hit their stop loss or take profit
            # Iterate through trades and test for stop loss or take profit
            for trade in trades:
                # Check for stop loss
                stop_loss_reached = test_for_stop_loss(historic_row, trade)
                # If Stop Loss reached, update
                if stop_loss_reached:
                    # Update the trade dictionary with 'trade_close_details' as the current historic row
                    trade['trade_close_details'] = historic_row
                    # Update the trade dictionary with 'trade_win' as False
                    trade['trade_win'] = False
                    # Append to completed trades
                    completed_trades.append(trade)
                    # Remove from trades list
                    trades.remove(trade)
                # Check for take profit
                take_profit_reached = test_for_take_profit(historic_row, trade)
                # If Take Profit reached, update
                if take_profit_reached:
                    # Update the trade dictionary with 'trade_close_details' as the current historic row
                    trade['trade_close_details'] = historic_row
                    # Update the trade dictionary with 'trade_win' as True
                    trade['trade_win'] = True
                    # Calculate the profit
                    profit = trade['take_profit'] * trade['lot_size']
                    # Add the profit to the current_balance
                    current_balance += profit
                    # Append to completed trades
                    completed_trades.append(trade)
                    # Remove from trades list
                    trades.remove(trade)
                # Step 2: Check to see if any trailing stops need to be updated
                new_stop_loss = check_trailing_stops(
                    historic_row=historic_row,
                    trade_row=trade,
                    raw_candlesticks=raw_candidate_candlesticks,
                    trailing_stop_column=trailing_stop_column,
                    trailing_stop_pips=trailing_stop_pips,
                    trailing_stop_percent=trailing_stop_percent,
                    pip_size=pip_size
                )
                # todo: If new_stop_loss is not None, update the trade dictionary with the new stop loss
                # Step 3: Check to see if any trailing take profits need to be updated
                new_take_profit = check_trailing_take_profits(
                    historic_row=historic_row,
                    trade_row=trade,
                    raw_candlesticks=raw_candidate_candlesticks,
                    trailing_take_profit_column=trailing_take_profit_column,
                    trailing_take_profit_pips=trailing_take_profit_pips,
                    trailing_take_profit_percent=trailing_take_profit_percent,
                    pip_size=pip_size
                )
                # todo: If new_take_profit is not None, update the trade dictionary with the new take profit

            # Step 4: Check the strategy dataframe to see if any new trades should be opened
            trade_outcome = False
            # Check if the historic_row human time is > than the strategy_row human time
            if historic_row['human_time'] > strategy_row['human_time']:
                # Branch based on the 'cancel_time' of the strategy_row
                # If cancel time is GTC, test the row
                if strategy_row['cancel_time'] == "GTC":
                    trade_outcome = test_for_new_trade(historic_row, strategy_row, cash, commission, risk_percent)
                # If cancel time is a datetime, check to see that the historic_row human time is < than the cancel time
                elif historic_row['human_time'] < strategy_row['cancel_time']:
                    trade_outcome = test_for_new_trade(historic_row, strategy_row, cash, commission, risk_percent)
            # If trade_outcome is True, add strategy_row to trades and remove from strategy_dataframe_dict
            if trade_outcome:
                # Add the historic_row data to the strategy_row in the column 'trade_open_details'
                strategy_row['trade_open_details'] = historic_row
                # Calculate the lot_size for the trade
                lot_size = helper_functions.calc_lot_size(
                    balance=current_balance,
                    risk_amount=risk_percent,
                    stop_loss=strategy_row['stop_loss'],
                    stop_price=strategy_row['stop_price'],
                    symbol=symbol,
                    exchange=exchange
                )
                # Add the lot_size to the strategy_row
                strategy_row['lot_size'] = lot_size
                # Subtract the amount risked from the balance
                current_balance -= current_balance * risk_percent
                # Append to trades
                trades.append(strategy_row)
                # Remove from strategy_dataframe_dict
                strategy_dataframe_dict.remove(strategy_row)
                break
    # Step 4: Calculate the results of the backtest
    # todo: Handle any open trades
    print(completed_trades)
    display_lib.display_backtest_results(
        raw_candles=raw_candidate_candlesticks,
        strategy_dataframe=strategy_dataframe,
        symbol=symbol,
        timeframe=candle_timeframe
    )
    return True


# Function to test a single row of historic data against an open trade and check if take_profit has been reached
def test_for_take_profit(historic_row, trade):
    """
    Function to test a single row of historic data against open trades and check if take_profit has been reached
    :param historic_row: dictionary of row data
    :param open_trades: list of open trades
    :return: Boolean. True if Take_Profit reached, False if not
    """

    # Check if the trade['order_type'] is a 'BUY_STOP'
    if trade['order_type'] == "BUY_STOP":
        # Check if the historic_row['high'] is >= than the trade['take_profit']
        if historic_row['high'] >= trade['take_profit']:
            # Return True
            return True
    # Check if the trade['order_type'] is a 'SELL_STOP'
    if trade['order_type'] == "SELL_STOP":
        # Check if the historic_row['low'] is <= than the trade['take_profit']
        if historic_row['low'] <= trade['take_profit']:
            # Return True
            return True
    return False


# Function to test a single row of historic data against open trade and check if stop_loss has been reached
def test_for_stop_loss(historic_row, trade):
    """
    Function to test a single row of historic data against open trades and check if stop_loss has been reached
    :param historic_row: dictionary of row data
    :param open_trades: list of open trades
    :return: Boolean. True if Stop_Loss reached, False if not
    """

    # Check if the trade['order_type'] is a 'BUY_STOP'
    if trade['order_type'] == "BUY_STOP":
        # Check if the historic_row['low'] is <= than the trade['stop_loss']
        if historic_row['low'] <= trade['stop_loss']:
            # Return True
            return True
    # Check if the trade['order_type'] is a 'SELL_STOP'
    if trade['order_type'] == "SELL_STOP":
        # Check if the historic_row['high'] is >= than the trade['stop_loss']
        if historic_row['high'] >= trade['stop_loss']:
            # Return True
            return True
    # Return False
    return False

# Function to test a single row of historic data against a strategy to determine if a new trade should be made
def test_for_new_trade(historic_row, strategy_dataframe_row, cash, commission, risk_percent):
    """
    Function to test a single row of historic data against a strategy row and determine if a trade should be made
    :param historic_row:
    :param strategy_dataframe_row:
    :param cash:
    :param commission:
    :param risk_percent:
    :param order_type:
    :return:
    """
    # A new trade should be made if the following conditions are met:
    # 1. If the order type is a 'BUY_STOP', the historic_row['high'] must be >= than the strategy_dataframe_row['stop_price'] AND the historic_row['low'] must be <= than the strategy_dataframe_row['stop_price']
    # 2. If the order type is a 'SELL_STOP', the historic_row['high'] must be >= than the strategy_dataframe_row['stop_price'] AND the historic_row['low'] must be <= than the strategy_dataframe_row['stop_price']
    #print(strategy_dataframe_row)
    # Branch based on the order type
    if strategy_dataframe_row['order_type'] == "BUY_STOP":
        # If the historic_row['high'] is >= than the strategy_dataframe_row['stop_price']
        # AND the historic_row['low'] is <= than the strategy_dataframe_row['stop_price'],
        # make a trade
        if historic_row['high'] >= strategy_dataframe_row['stop_price'] and historic_row['low'] <= strategy_dataframe_row['stop_price']:
            print("BUY_STOP Trade Entered!!!")
            return True
    elif strategy_dataframe_row['order_type'] == "SELL_STOP":
        # If the historic_row['low'] is <= than the strategy_dataframe_row['stop_price']
        # AND the historic_row['high'] is >= than the strategy_dataframe_row['stop_price'],
        # make a trade
        if historic_row['low'] <= strategy_dataframe_row['stop_price'] and historic_row['high'] >= strategy_dataframe_row['stop_price']:
            print("SELL_STOP Trade Entered!!!")
            return True
    return False


# Function to check trailing stops
def check_trailing_stops(historic_row, trade_row, raw_candlesticks, trailing_stop_column=None, trailing_stop_pips=None, trailing_stop_percent=None, pip_size=None):
    # Set a default new stop_loss price
    new_stop_loss = None
    # Pass if no trailing stops provided
    if trailing_stop_column is None and trailing_stop_pips is None and trailing_stop_percent is None:
        pass
    # Error check
    if trailing_stop_pips is not None and pip_size is None:
        raise ValueError("If trailing_stop_pips is provided, pip_size must also be provided")

    # Branch based on the trailing stop inputs
    # Trailing stop pips
    if trailing_stop_pips:
        # Calculate the trailing stop size
        trailing_stop_size = trailing_stop_pips * pip_size
        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            trailing_stop_price = historic_row['low'] + trailing_stop_size
            # Check if the historic_row['high'] is >= than the stop_loss
            if trailing_stop_price > trade_row['stop_loss']:
                new_stop_loss = trailing_stop_price
        elif trade_row['order_type'] == "SELL_STOP":
            trailing_stop_price = historic_row['high'] - trailing_stop_size
            # Check if the historic_row['low'] is <= than the stop_loss
            if trailing_stop_price < trade_row['stop_loss']:
                new_stop_loss = trailing_stop_price
    # Trailing stop percent
    elif trailing_stop_percent:
        # Calculate the trailing stop size
        trailing_stop_size = trailing_stop_percent * trade_row['stop_price']
        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            trailing_stop_price = historic_row['low'] + trailing_stop_size
            # Check if the historic_row['high'] is >= than the stop_loss
            if trailing_stop_price > trade_row['stop_loss']:
                new_stop_loss = trailing_stop_price
        elif trade_row['order_type'] == "SELL_STOP":
            trailing_stop_price = historic_row['high'] - trailing_stop_size
            # Check if the historic_row['low'] is <= than the stop_loss
            if trailing_stop_price < trade_row['stop_loss']:
                new_stop_loss = trailing_stop_price
    # Trailing stop column
    elif trailing_stop_column:
        # Get the current row in the raw candlesticks dataframe based upon the human time of the historic row
        for index, row in raw_candlesticks.iterrows():
            if historic_row['human_time'] > row['human_time']:
                # Get the value of the index-1 column
                trailing_stop_price = raw_candlesticks.loc[index-1, trailing_stop_column]
                break


        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            # Check if the historic_row['high'] is >= than the stop_loss
            if trailing_stop_price > trade_row['stop_loss']:
                new_stop_loss = trailing_stop_price
        elif trade_row['order_type'] == "SELL_STOP":
            # Check if the historic_row['low'] is <= than the stop_loss
            if trailing_stop_price < trade_row['stop_loss']:
                new_stop_loss = trailing_stop_price
    return new_stop_loss


# Function to check trailing take profits
def check_trailing_take_profits(historic_row, trade_row, raw_candlesticks, trailing_take_profit_column=None, trailing_take_profit_pips=None, trailing_take_profit_percent=None, pip_size=None):
    # Set a default new take_profit price
    new_take_profit = None
    # Pass if no trailing take profits provided
    if trailing_take_profit_column is None and trailing_take_profit_pips is None and trailing_take_profit_percent is None:
        pass
    # Error check
    if trailing_take_profit_pips is not None and pip_size is None:
        raise ValueError("If trailing_take_profit_pips is provided, pip_size must also be provided")

    # Branch based on the trailing take profit inputs
    # Trailing take profit pips
    if trailing_take_profit_pips:
        # Calculate the trailing take profit size
        trailing_take_profit_size = trailing_take_profit_pips * pip_size
        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            trailing_take_profit_price = historic_row['high'] + trailing_take_profit_size
            # Check if the historic_row['high'] is >= than the take_profit
            if trailing_take_profit_price > trade_row['take_profit']:
                new_take_profit = trailing_take_profit_price
        elif trade_row['order_type'] == "SELL_STOP":
            trailing_take_profit_price = historic_row['low'] - trailing_take_profit_size
            # Check if the historic_row['low'] is <= than the take_profit
            if trailing_take_profit_price < trade_row['take_profit']:
                new_take_profit = trailing_take_profit_price
    # Trailing take profit percent
    elif trailing_take_profit_percent:
        # Calculate the trailing take profit size
        trailing_take_profit_size = trailing_take_profit_percent * trade_row['stop_price']
        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            trailing_take_profit_price = historic_row['high'] + trailing_take_profit_size
            # Check if the historic_row['high'] is >= than the take_profit
            if trailing_take_profit_price > trade_row['take_profit']:
                new_take_profit = trailing_take_profit_price
        elif trade_row['order_type'] == "SELL_STOP":
            trailing_take_profit_price = historic_row['low'] - trailing_take_profit_size
            # Check if the historic_row['low'] is <= than the take_profit
            if trailing_take_profit_price < trade_row['take_profit']:
                new_take_profit = trailing_take_profit_price
    # Trailing take profit column
    elif trailing_take_profit_column:
        # Get the current row in the raw candlesticks dataframe based upon the human time of the historic row
        for index, row in raw_candlesticks.iterrows():
            if historic_row['human_time'] > row['human_time']:
                # Get the value of the index-1 column
                trailing_take_profit_price = raw_candlesticks.loc[index-1, trailing_take_profit_column]
                break


        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            # Check if the historic_row['high'] is >= than the take_profit
            if trailing_take_profit_price > trade_row['take_profit']:
                new_take_profit = trailing_take_profit_price
        elif trade_row['order_type'] == "SELL_STOP":
            # Check if the historic_row['low'] is <= than the take_profit
            if trailing_take_profit_price < trade_row['take_profit']:
                new_take_profit = trailing_take_profit_price
    return new_take_profit