import itertools
import multiprocessing
from datetime import timedelta

import numpy
import numpy as np
from backtesting import Backtest

import display_lib
import mt5_lib
import pandas
import os
import helper_functions
from backtesting_py_strategies import ema_cross
from strategies import macd_crossover_strategy
from tqdm import tqdm


# Function to multi-optimize a strategy
def multi_optimize(strategy, cash, commission, symbols, timeframes, exchange, time_to_test, params, forex=False,
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
    :param forex: boolean to identify if the strategy is a forex strategy
    :param risk_percent: decimal value of the percentage of the account to risk per trade
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
    :param strategy: string of the strategy to be tested
    :param cash: Start cash
    :param symbol: string of the symbol to be tested
    :param timeframe: string of the timeframe to be tested
    :param exchange: string identifying the exchange to retreive data from
    :param optimize: boolean to identify if the strategy should be optimized
    :param save: boolean to identify if the strategy should be saved
    :param plot_save_location: string of the location to save the plot
    :param result_save_location: string of the location to save the results
    :param params: dictionary of parameters to be optimized
    :param forex: boolean to identify if the strategy is a forex strategy
    :param risk_percent: decimal value of the percentage of the account to risk per trade
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


# Define an overarching forex backtest function, including the ability optimize parameters, symbols, timeframes, and use
# multiprocessing
def forex_backtest(strategy, cash, commission, symbols, timeframes, time_to_test, risk_percent, strategy_params=[],
                   exchange="mt5", optimize_params=False, optimize_take_profit=False, optimize_stop_loss=False,
                   optimize_order_cancel_time=False, display_results=False, save_results=False,
                   trailing_stop_column=None, trailing_stop_pips=None, trailing_stop_percent=None,
                   trailing_take_profit_column=None, trailing_take_profit_pips=None, trailing_take_profit_percent=None,
                   optimize_trailing_stop_pips=False, optimize_trailing_stop_percent=False):
    # Retrieve strategy dataframe
    if strategy == "MACD_Crossover":
        pass
    else:
        raise ValueError("Strategy not supported")
    # Results
    results = []
    # Arguments List
    args_list = []
    # Iterate through the symbols
    for symbol in symbols:
        symbol_check = symbol.split(".")
        if symbol_check[0] == "ETHUSD":
            pip_size = 0.01
        else:
            # Get the pip_size
            pip_size = mt5_lib.get_pip_size(symbol)
        # Get the contract size for a symbol
        contract_size = mt5_lib.get_contract_size(symbol=symbol)
        # Iterate through the timeframes
        for timeframe in timeframes:
            if exchange == "mt5":
                # Get historic data from exchange. Keep this single threaded
                historic_data = mt5_lib.query_historic_data_by_time(
                    symbol=symbol,
                    timeframe="M1",
                    time_range=time_to_test
                )
                # Get raw candlestick data for strategy
                raw_strategy_candles = mt5_lib.query_historic_data_by_time(
                    symbol=symbol,
                    timeframe=timeframe,
                    time_range=time_to_test
                )
            else:
                raise ValueError("Exchange not supported")
            # Create a grid search based on the parameters
            grid_search = create_grid_search(
                params=strategy_params,
                optimize_params=optimize_params,
                optimize_take_profit=optimize_take_profit,
                optimize_stop_loss=optimize_stop_loss
            )

            print("Generating backtests")
            print(f"Total number of backtests: {len(grid_search)}")
            with tqdm(total=len(grid_search)) as pbar:
                for parameters in grid_search:
                    pbar.update(1)
                    # Pass the grid search to the strategy
                    if strategy == "MACD_Crossover":
                        strategy_candles = macd_crossover_strategy.macd_crossover_strategy(
                            time_to_test=time_to_test,
                            time_to_cancel=parameters[5],
                            macd_fast=parameters[2],
                            macd_slow=parameters[3],
                            macd_signal=parameters[4],
                            dataframe=raw_strategy_candles,
                            stop_loss_multiplier=parameters[1],
                            take_profit_multiplier=parameters[0]
                        )

                    else:
                        raise ValueError("Strategy not supported")
                    # If the strategy dataframe is empty, skip this iteration
                    if strategy_candles is False:
                        print(f"Params: {parameters}, Strategy dataframe: False")
                        profit = 0
                    elif len(strategy_candles) == 0:
                        print(f"Params: {parameters}, Strategy dataframe: Empty")
                        profit = 0
                    else:
                        # Get the last candle
                        last_candle = strategy_candles.iloc[-1]
                        # If optimize_order_cancel_timme is True, add another for loop to iterate through the strategy
                        # dataframe
                        if optimize_order_cancel_time:
                            for i in range(5, 1440):
                                # Replace the column 'cancel_time' with the new cancel time of i added to 'human_time'
                                strategy_candles['cancel_time'] = strategy_candles['human_time'] + timedelta(minutes=i)
                                # Create a tuple of the arguments
                                args_tuple = (strategy_candles, raw_strategy_candles, cash, commission, symbol,
                                              historic_data, pip_size, contract_size, risk_percent)
                                # Append to args_list
                                args_list.append(args_tuple)
                        elif optimize_trailing_stop_pips:
                            for i in range(1, 2000):
                                # Replace the column 'trailing_stop_pips' with the new value of i
                                args_tuple = (strategy_candles, raw_strategy_candles, cash, commission, symbol,
                                              historic_data, pip_size, contract_size, risk_percent,
                                              trailing_stop_column, i, trailing_stop_percent,
                                              trailing_take_profit_column, trailing_take_profit_pips,
                                              trailing_take_profit_percent)
                                # Append to args_list
                                args_list.append(args_tuple)
                        elif optimize_trailing_stop_percent:
                            for i in range(1, 50):
                                # Replace the column 'trailing_stop_percent' with the new value of i
                                args_tuple = (strategy_candles, raw_strategy_candles, cash, commission, symbol,
                                              historic_data, pip_size, contract_size, risk_percent,
                                              trailing_stop_column, trailing_stop_pips, i,
                                              trailing_take_profit_column, trailing_take_profit_pips,
                                              trailing_take_profit_percent)
                                # Append to args_list
                                args_list.append(args_tuple)
                        else:
                            # Create an args_tuple
                            args_tuple = (strategy_candles, raw_strategy_candles, cash, commission, symbol,
                                          historic_data, pip_size, contract_size, risk_percent, trailing_stop_column,
                                          trailing_stop_pips, trailing_stop_percent, trailing_take_profit_column,
                                          trailing_take_profit_pips, trailing_take_profit_percent)
                            # Append to args_list
                            args_list.append(args_tuple)

            if len(args_list) > 0:
                print("Assigning processing cores and processing backtests")
                # Create a pool of workers
                with multiprocessing.Pool(10) as pool:
                    backtest_results = pool.starmap(forex_backtest_run, tqdm(args_list, total=len(args_list)))
                    # Extract the profit from backtest_results
                    for result in backtest_results:
                        # Update the result
                        result['symbol'] = symbol
                        result['timeframe'] = timeframe
                        # Append to results
                        results.append(result)
    # Iterate through the results, and find the result with the highest profit
    best_result = None
    for result in results:
        if best_result is None:
            best_result = result
        elif result['profit'] > best_result['profit']:
            best_result = result
    # Print the best result
    print(f"Best result: {best_result['profit']}")
    # Reprocess the best result to get a display dataframe
    if display_results:
        print("Generating results display")
        # Extract the proposed trades
        proposed_trades = best_result['proposed_trades']
        # Turn into a dataframe
        proposed_trades = pandas.DataFrame(proposed_trades)
        # Write to JSON
        proposed_trades.to_json("proposed_trades.json")
        # Output to JSON
        display_backtest_results(
            backtest_results=best_result,
            raw_candlesticks=best_result['raw_strategy_candles'],
            strategy_candlesticks=best_result['proposed_trades'],
        )

    # Pass the result to display_backtest_results

    # Return the results
    return results


# Function to backtest a FOREX strategy
def forex_backtest_run(strategy_dataframe, raw_strategy_candlesticks, cash, commission, symbol, historic_data, pip_size,
                       contract_size, risk_percent, trailing_stop_column=None, trailing_stop_pips=None,
                       trailing_stop_percent=None, trailing_take_profit_column=None, trailing_take_profit_pips=None,
                       trailing_take_profit_percent=None, display_results=False, parameters=None):
    """
    Function to backtest a FOREX strategy. Runs a single pass of a backtest. Set up to be multi-processable, so all
    all information must be passed into function.
    :param strategy_dataframe: dataframe of the strategy candles (i.e. the trades)
    :param raw_strategy_candlesticks: dataframe of the candlesticks used to generate the strategy dataframe
    :param cash: float of the starting cash
    :param commission: float of the commission per trade
    :param symbol: string of the symbol being traded
    :param historic_data: dataframe of 1 Minute candlesticks over the period of the strategy
    :param pip_size: float of the pip size of a symbol
    :param contract_size: contract size for converting a lot into a dollar value
    :param risk_percent: float of the amount of the balance being risked for each trade
    :param trailing_stop_column: string of the column the trailing stop should be pinned to
    :param trailing_stop_pips: float of the number of pips the trailing stop should be applied against
    :param trailing_stop_percent: float of the percent the trailing stop should be applied against
    :param trailing_take_profit_column: string of the column the trailing take profit should be pinned to
    :param trailing_take_profit_pips: float of the number of pips the trailing take profit should be applied against
    :param trailing_take_profit_percent: float of the percent the trailing take profit should be applied against
    :param display_results: boolean of whether to display the results of the backtest
    :param parameters: dictionary of parameters to be passed to the strategy
    :return: dictionary of the results of the backtest
    """
    ### Pseudocode ###
    # 1. Get data pricing data from exchange
    # 2. Iterate through the pricing data and apply against the strategy dataframe. Make sure to store every trade.
    # 3. Calculate the results of the backtest
    # 4. Return the results of the backtest
    # 5. Provide option to display results of the backtest
    # 6. Provide option to save results of the backtest
    # Add a column to strategy_dataframe called 'trailing_stop_update'
    strategy_dataframe['trailing_stop_update'] = np.empty((len(strategy_dataframe), 0)).tolist()
    # Add a column to strategy_dataframe called 'trailing_take_profit_update'
    strategy_dataframe['trailing_take_profit_update'] = np.empty((len(strategy_dataframe), 0)).tolist()
    # Add a column to strategy_dataframe called 'original_stop_loss', setting it to the strategy stop loss
    strategy_dataframe['original_stop_loss'] = strategy_dataframe['stop_loss']
    # Add a column to strategy_dataframe called 'original_take_profit', setting it to the strategy take profit
    strategy_dataframe['original_take_profit'] = strategy_dataframe['take_profit']
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
    for historic_row in historic_data_dict:
        # Step 1: Check trades for any updates
        for trade in trades:
            # Step 1.1: Check to see if any trailing stops need to be updated
            new_stop_loss = check_trailing_stops(
                historic_row=historic_row,
                trade_row=trade,
                raw_candlesticks=raw_strategy_candlesticks,
                trailing_stop_column=trailing_stop_column,
                trailing_stop_pips=trailing_stop_pips,
                trailing_stop_percent=trailing_stop_percent,
                pip_size=pip_size
            )
            # If a new stop loss is returned, update the trade
            if new_stop_loss["new_stop_loss"] is not None:
                # Create a dictionary to store the update
                update = {
                    'time': historic_row['time'],
                    'human_time': historic_row['human_time'],
                    'new_stop_loss': new_stop_loss["new_stop_loss"],
                    'previous_stop_loss': trade['stop_loss'],
                    'historic_row': historic_row,
                    'details': new_stop_loss
                }
                # Add an update to the trade dictionary recording the stop loss change
                trade['trailing_stop_update'].append(update)
                # Update the trade dictionary with the new stop loss
                trade['stop_loss'] = new_stop_loss["new_stop_loss"]
            # Step 1.2: Check to see if any trailing take profits need to be updated
            new_take_profit = check_trailing_take_profits(
                historic_row=historic_row,
                trade_row=trade,
                raw_candlesticks=raw_strategy_candlesticks,
                trailing_take_profit_column=trailing_take_profit_column,
                trailing_take_profit_pips=trailing_take_profit_pips,
                trailing_take_profit_percent=trailing_take_profit_percent,
                pip_size=pip_size
            )
            if new_take_profit["new_take_profit"] is not None:
                # Create a dictionary to store the update
                update = {
                    'time': historic_row['time'],
                    'human_time': historic_row['human_time'],
                    'new_take_profit': new_take_profit,
                    'previous_take_profit': trade['take_profit'],
                    'historic_row': historic_row,
                    'details': new_take_profit
                }
                # Add an update to the trade dictionary recording the take profit change
                trade['trailing_take_profit_update'].append(update)
                # Update the trade dictionary with the new take profit
                trade['take_profit'] = new_take_profit["new_take_profit"]
            # Step 1.3: Check to see if any stop losses have been reached
            stop_loss_reached = test_for_stop_loss(historic_row, trade)
            # If Stop Loss reached, update
            if stop_loss_reached:
                # Update the trade dictionary with 'trade_close_details' as the current historic row
                trade['trade_close_details'] = historic_row
                trade['closing_price'] = trade['stop_loss']
                trade['closing_time'] = historic_row['human_time']
                profit = calculate_profit(trade, "stop_loss", contract_size)
                if profit > 0:
                    trade['trade_win'] = True
                    current_balance += profit
                else:
                    trade['trade_win'] = False
                # Append to completed trades
                completed_trades.append(trade)
                # Remove from trades list
                trades.remove(trade)
            else:
                # Step 1.4: Check to see if Take Profit has been reached
                take_profit_reached = test_for_take_profit(historic_row, trade)
                # If Take Profit reached, update
                if take_profit_reached:
                    # Update the trade dictionary with 'trade_close_details' as the current historic row
                    trade['trade_close_details'] = historic_row
                    trade['closing_price'] = trade['take_profit']
                    trade['closing_time'] = historic_row['human_time']
                    # Calculate the profit
                    profit = calculate_profit(trade, "take_profit", contract_size)
                    if profit > 0:
                        trade['trade_win'] = True
                        current_balance += profit
                    else:
                        trade['trade_win'] = False
                    # Append to completed trades
                    completed_trades.append(trade)
                    # Remove from trades list
                    trades.remove(trade)

        # Step 2: Check the strategy to see if any new trades should be opened
        for strategy_row in strategy_dataframe_dict:
            # Make sure that only valid strategy rows are being processed
            if historic_row['human_time'] >= strategy_row['human_time']:
                if historic_row['human_time'] < strategy_row['cancel_time'] or strategy_row['cancel_time'] == "GTC":
                    # Step 2.1: Check the strategy dataframe to see if any new trades should be opened
                    trade_outcome = False
                    # Check if the historic_row human time is > than the strategy_row human time
                    if historic_row['human_time'] > strategy_row['human_time']:
                        # Branch based on the 'cancel_time' of the strategy_row
                        # If cancel time is GTC, test the row
                        if strategy_row['cancel_time'] == "GTC":
                            trade_outcome = test_for_new_trade(historic_row, strategy_row, cash, commission,
                                                               risk_percent)
                        # If cancel time is a datetime, check to see that the historic_row human time is < than the cancel time
                        elif historic_row['human_time'] < strategy_row['cancel_time']:
                            trade_outcome = test_for_new_trade(historic_row, strategy_row, cash, commission,
                                                               risk_percent)
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
                            pip_size=pip_size,
                            base_currency="USD"
                        )
                        # Add the lot_size to the strategy_row
                        strategy_row['lot_size'] = lot_size
                        # Add in the original stop_loss and take_profit
                        strategy_row['original_stop_loss'] = strategy_row['stop_loss']
                        strategy_row['original_take_profit'] = strategy_row['take_profit']
                        # Add in the original starting time
                        strategy_row['original_start_time'] = historic_row['human_time']
                        # Subtract the amount risked from the balance
                        current_balance -= current_balance * risk_percent
                        # Append to trades
                        trades.append(strategy_row)
                        # Remove from strategy_dataframe_dict
                        strategy_dataframe_dict.remove(strategy_row)
                        break
    # Step 3: Calculate the results of the backtest
    backtest_results = calculate_backtest_results(completed_trades, contract_size, parameters,
                                                  raw_strategy_candlesticks, strategy_dataframe)

    # todo: Handle any open trades

    return backtest_results


# Function to display the results of a backtest
def display_backtest_results(backtest_results, raw_candlesticks, strategy_candlesticks):
    # Extract the win_objects from the backtest_results
    win_objects = backtest_results['win_objects']
    # Convert to a dataframe
    win_dataframe = pandas.DataFrame(win_objects)
    # Write to json
    win_dataframe.to_json("raw_win_dataframe_raw.json")
    # Extract the columns trade_id, order_type, lot_size, closing_stop_price, closing_price, closing_time, profit,
    # trade_trailing_stop, trade_trailing_take_profit
    if len(win_dataframe) > 0:
        win_dataframe = win_dataframe[
            ['trade_id', 'order_type', 'lot_size', 'closing_stop_price', 'closing_price', 'closing_time', 'profit']]
    # Create a figure of the win dataframe
    win_dataframe_figure = display_lib.dataframe_to_table(win_dataframe, "Win Objects")
    # Extract the loss_objects from the backtest_results
    loss_objects = backtest_results['loss_objects']
    # Convert to a dataframe
    loss_dataframe = pandas.DataFrame(loss_objects)
    # Write to json
    loss_dataframe.to_json("raw_loss_dataframe_raw.json")
    if len(loss_dataframe) > 0:
        # Extract the columns trade_id, order_type, lot_size, closing_stop_price, closing_price, closing_time, profit,
        # trade_trailing_stop, trade_trailing_take_profit
        loss_dataframe = loss_dataframe[
            ['trade_id', 'order_type', 'lot_size', 'closing_stop_price', 'closing_price', 'closing_time', 'profit']]
    # Create a figure of the loss dataframe
    loss_dataframe_figure = display_lib.dataframe_to_table(loss_dataframe, "Loss Objects")
    # Extract the human_time, open, high, low, close, order_type, original_stop_loss,
    # original_take_profit, and stop_price from the strategy_candlesticks
    proposed_trades = strategy_candlesticks[
        ['human_time', 'open', 'high', 'low', 'close','order_type', 'original_stop_loss',
         'original_take_profit', 'stop_price']
    ]


    # Create a table of the proposed trades
    proposed_trades_table = display_lib.dataframe_to_table(
        dataframe=proposed_trades,
        title="Proposed Trades"
    )

    # Create a figure of the proposed trades
    proposed_trades_figure = display_lib.proposed_trades_graph(
        raw_candlesticks=raw_candlesticks,
        proposed_trades=strategy_candlesticks
    )
    # Create a figure of the completed trades
    completed_trades_figure = display_lib.completed_trades(
        raw_candles=raw_candlesticks,
        backtest_results=backtest_results
    )
    # Display the figure
    display_lib.display_backtest(
        proposed_trades=proposed_trades_figure,
        completed_trades=completed_trades_figure,
        win_objects=win_dataframe_figure,
        loss_objects=loss_dataframe_figure,
        proposed_trades_table=proposed_trades_table
    )


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
    :param trade: the current trade being assessed
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
    :param historic_row: dataframe row of the 1 minute timeframe being tested
    :param strategy_dataframe_row: dataframe row of the strategy being tested
    :param cash: float of the current cash balance
    :param commission: float of the percentage of each trade taken in commission
    :param risk_percent: float of the percentage of the cash balance to risk on each trade
    :return: boolean of whether a new trade should be made
    """
    # A new trade should be made if the following conditions are met:
    # 1. If the order type is a 'BUY_STOP', the historic_row['high'] must be >= than the strategy_dataframe_row['stop_price'] AND the historic_row['low'] must be <= than the strategy_dataframe_row['stop_price']
    # 2. If the order type is a 'SELL_STOP', the historic_row['high'] must be >= than the strategy_dataframe_row['stop_price'] AND the historic_row['low'] must be <= than the strategy_dataframe_row['stop_price']
    # print(strategy_dataframe_row)
    # Branch based on the order type
    if strategy_dataframe_row['order_type'] == "BUY_STOP":
        # If the historic_row['high'] is >= than the strategy_dataframe_row['stop_price']
        # AND the historic_row['low'] is <= than the strategy_dataframe_row['stop_price'],
        # make a trade
        if historic_row['high'] >= strategy_dataframe_row['stop_price'] >= historic_row['low']:
            # print("BUY_STOP Trade Entered!!!")
            return True
    elif strategy_dataframe_row['order_type'] == "SELL_STOP":
        # If the historic_row['low'] is <= than the strategy_dataframe_row['stop_price']
        # AND the historic_row['high'] is >= than the strategy_dataframe_row['stop_price'],
        # make a trade
        if historic_row['low'] <= strategy_dataframe_row['stop_price'] <= historic_row['high']:
            # print("SELL_STOP Trade Entered!!!")
            return True
    return False


# Function to check trailing stops
def check_trailing_stops(historic_row, trade_row, raw_candlesticks, trailing_stop_column=None, trailing_stop_pips=None,
                         trailing_stop_percent=None, pip_size=None):
    # Set a default new stop_loss price
    new_stop_loss = {
        'new_stop_loss': None,
        'stop_loss_type': "",
        'stop_loss_details': None
    }
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
            # Check if the historic_row['high'] - trade_row['stop_loss'] is > than the trailing_stop_size
            if historic_row['high'] - trade_row['stop_loss'] > trailing_stop_size:
                trailing_stop_price = historic_row['high'] - trailing_stop_size
                # Check if the trailing stop price is > than the current historic_row['high']
                if trailing_stop_price > historic_row['high']:
                    # Set the trailing_stop_price to the historic_row['high']
                    trailing_stop_price = historic_row['high']
                    print(f"Error in trailing stop pip trail function")
                # Check if the trailing_stop_price is > than the current stop loss
                if trailing_stop_price > trade_row['stop_loss']:
                    new_stop_loss["new_stop_loss"] = trailing_stop_price
                    new_stop_loss["stop_loss_type"] = "TRAILING_STOP_PIPS"
                    new_stop_loss["stop_loss_details"] = trailing_stop_size
        elif trade_row['order_type'] == "SELL_STOP":
            # Check if the trade_row['stop_loss'] - historic_row['low'] is > than the trailing_stop_size
            if trade_row['stop_loss'] - historic_row['low'] > trailing_stop_size:
                trailing_stop_price = historic_row['low'] + trailing_stop_size
                # Check if the trailing stop price is < than the current historic_row['low']
                if trailing_stop_price < historic_row['low']:
                    # Set the trailing_stop_price to the historic_row['low']
                    trailing_stop_price = historic_row['low']
                # Check if the historic_row['low'] is < than the stop_loss
                if trailing_stop_price < trade_row['stop_loss']:
                    new_stop_loss["new_stop_loss"] = trailing_stop_price
                    new_stop_loss["stop_loss_type"] = "TRAILING_STOP_PIPS"
                    new_stop_loss["stop_loss_details"] = trailing_stop_size
    # Trailing stop percent
    elif trailing_stop_percent:
        # Calculate the trailing stop size
        trailing_stop_size = trailing_stop_percent * trade_row['stop_price']
        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            trailing_stop_price = historic_row['high'] - trailing_stop_size
            # Check if the historic_row['high'] is > than the stop_loss
            if trailing_stop_price > trade_row['stop_loss']:
                new_stop_loss["new_stop_loss"] = trailing_stop_price
                new_stop_loss["stop_loss_type"] = "TRAILING_STOP_PERCENT"
                new_stop_loss["stop_loss_details"] = trailing_stop_size
        elif trade_row['order_type'] == "SELL_STOP":
            trailing_stop_price = historic_row['low'] + trailing_stop_size
            # Check if the historic_row['low'] is < than the stop_loss
            if trailing_stop_price < trade_row['stop_loss']:
                new_stop_loss["new_stop_loss"] = trailing_stop_price
                new_stop_loss["stop_loss_type"] = "TRAILING_STOP_PERCENT"
                new_stop_loss["stop_loss_details"] = trailing_stop_size
    # Trailing stop column
    elif trailing_stop_column:
        trailing_stop_price = None
        # Add a column called candle_end_time to the raw candlesticks dataframe which is the human time of the next
        # candle minus 1 second
        raw_candlesticks['candle_end_time'] = raw_candlesticks['human_time'].shift(-1) - timedelta(seconds=1)
        # Get the current row in the raw candlesticks dataframe based upon the human time of the historic row
        for index, row in raw_candlesticks.iterrows():
            if row['human_time'] < historic_row['human_time'] <= row['candle_end_time']:
                # Get the value of the index-1 column
                trailing_stop_price = raw_candlesticks.loc[index - 1, trailing_stop_column]
                new_stop_loss["stop_loss_details"] = raw_candlesticks.loc[index - 1]
                break

        if trailing_stop_price:
            # Branch based on the order type
            if trade_row['order_type'] == "BUY_STOP":
                # Check if the historic_row['high'] is >= than the stop_loss
                if trailing_stop_price > trade_row['stop_loss']:
                    new_stop_loss["new_stop_loss"] = trailing_stop_price
                    new_stop_loss["stop_loss_type"] = "TRAILING_STOP_COLUMN"
            elif trade_row['order_type'] == "SELL_STOP":
                # Check if the historic_row['low'] is <= than the stop_loss
                if trailing_stop_price < trade_row['stop_loss']:
                    new_stop_loss["new_stop_loss"] = trailing_stop_price
                    new_stop_loss["stop_loss_type"] = "TRAILING_STOP_COLUMN"
    return new_stop_loss


# Function to check trailing take profits
def check_trailing_take_profits(historic_row, trade_row, raw_candlesticks, trailing_take_profit_column=None,
                                trailing_take_profit_pips=None, trailing_take_profit_percent=None, pip_size=None):
    # Set a default new take_profit price
    new_take_profit = {
        "new_take_profit": None,
        "take_profit_type": None,
        "take_profit_details": None
    }
    # Pass if no trailing take profits provided
    if trailing_take_profit_column is None and trailing_take_profit_pips is None and trailing_take_profit_percent is \
            None:
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
            # Check if the historic_row['high'] + trailing_take_profit_size is > than the take_profit
            if trailing_take_profit_price > trade_row['take_profit']:
                new_take_profit["new_take_profit"] = trailing_take_profit_price
                new_take_profit["take_profit_type"] = "TRAILING_TAKE_PROFIT_PIPS"
                new_take_profit["take_profit_details"] = trailing_take_profit_size
        elif trade_row['order_type'] == "SELL_STOP":
            trailing_take_profit_price = historic_row['low'] - trailing_take_profit_size
            # Check if the historic_row['low'] is < than the take_profit
            if trailing_take_profit_price < trade_row['take_profit']:
                new_take_profit["new_take_profit"] = trailing_take_profit_price
                new_take_profit["take_profit_type"] = "TRAILING_TAKE_PROFIT_PIPS"
                new_take_profit["take_profit_details"] = trailing_take_profit_size
    # Trailing take profit percent
    elif trailing_take_profit_percent:
        # Calculate the trailing take profit size
        trailing_take_profit_size = trailing_take_profit_percent * trade_row['stop_price']
        # Branch based on the order type
        if trade_row['order_type'] == "BUY_STOP":
            trailing_take_profit_price = historic_row['high'] + trailing_take_profit_size
            # Check if the historic_row['high'] is > than the take_profit
            if trailing_take_profit_price > trade_row['take_profit']:
                new_take_profit["new_take_profit"] = trailing_take_profit_price
                new_take_profit["take_profit_type"] = "TRAILING_TAKE_PROFIT_PERCENT"
                new_take_profit["take_profit_details"] = trailing_take_profit_size
        elif trade_row['order_type'] == "SELL_STOP":
            trailing_take_profit_price = historic_row['low'] - trailing_take_profit_size
            # Check if the historic_row['low'] is < than the take_profit
            if trailing_take_profit_price < trade_row['take_profit']:
                new_take_profit["new_take_profit"] = trailing_take_profit_price
                new_take_profit["take_profit_type"] = "TRAILING_TAKE_PROFIT_PERCENT"
                new_take_profit["take_profit_details"] = trailing_take_profit_size
    # Trailing take profit column
    elif trailing_take_profit_column:
        trailing_take_profit_price = None
        # Add a column called candle_end_time to the raw candlesticks dataframe which is the human time of the
        # previous candle minus 1 second
        raw_candlesticks['candle_end_time'] = raw_candlesticks['human_time'].shift(-1) - timedelta(seconds=1)
        # Get the current row in the raw candlesticks dataframe based upon the human time of the historic row
        for index, row in raw_candlesticks.iterrows():
            if row['human_time'] < historic_row['human_time'] <= row['candle_end_time']:
                # Get the value of the index-1 column
                trailing_take_profit_price = raw_candlesticks.loc[index - 1, trailing_take_profit_column]
                new_take_profit["take_profit_details"] = raw_candlesticks.loc[index - 1]
                break

        if trailing_take_profit_price:
            # Branch based on the order type
            if trade_row['order_type'] == "BUY_STOP":
                # Check if the historic_row['high'] is > than the take_profit
                if trailing_take_profit_price > trade_row['take_profit']:
                    new_take_profit["new_take_profit"] = trailing_take_profit_price
                    new_take_profit["take_profit_type"] = "TRAILING_TAKE_PROFIT_COLUMN"
            elif trade_row['order_type'] == "SELL_STOP":
                # Check if the historic_row['low'] is <= than the take_profit
                if trailing_take_profit_price < trade_row['take_profit']:
                    new_take_profit["new_take_profit"] = trailing_take_profit_price
                    new_take_profit["take_profit_type"] = "TRAILING_TAKE_PROFIT_COLUMN"
    return new_take_profit


# Function to calculate backtest results
def calculate_backtest_results(results_dict, contract_size, parameters, raw_strategy_candles, proposed_trades):
    """
    Function to calculate backtest results
    :param results_dict: dictionary of all the completed trade actions
    :return: dictionary of backtest results
    """
    # Create an ID number for trades in backtest
    trade_id = 0
    # Convert results_dict to a dataframe
    results_df = pandas.DataFrame.from_dict(results_dict)
    pandas.set_option('display.max_columns', None)
    # Write the results to a json file
    # results_df.to_json("results.json")
    # Get the total number of trades
    trades = len(results_dict)
    # Get the total number of wins which will be when 'trade_win' is True
    wins = 0
    # Get the total number of losses which will be when 'trade_win' is False
    losses = 0
    # Create objects for the trade details
    win_objects = []
    loss_objects = []
    # Calculate the profit/loss
    profit = 0.00
    for index, row in results_df.iterrows():
        if row['trade_win']:
            wins = len(results_df[results_df['trade_win'] == True])
            if row['order_type'] == "BUY_STOP":
                row_profit = (row['closing_price'] - row['stop_price']) * row['lot_size'] * contract_size
            elif row['order_type'] == "SELL_STOP":
                row_profit = (row['stop_price'] - row['closing_price']) * row['lot_size'] * contract_size
            profit += row_profit
            # Create a win_object
            # todo: Manage trailing stops
            win_object = {
                "trade_id": trade_id,
                "order_type": row['order_type'],
                "lot_size": row['lot_size'],
                "closing_stop_price": row['stop_price'],
                "closing_take_profit": row['take_profit'],
                "closing_stop_loss": row['stop_loss'],
                "starting_stop_loss": row['original_stop_loss'],
                "starting_take_profit": row['original_take_profit'],
                "ending_stop_loss": row['stop_loss'],
                "ending_profit_price": row['take_profit'],
                "closing_price": row['closing_price'],
                "closing_time": row['closing_time'],
                "profit": row_profit,
                "order_open_time": row['human_time'],
                "trade_open_time": row['original_start_time'],
                "trade_close_time": row['closing_time'],
                "trade_trailing_stop": row['trailing_stop_update'],
                "trade_trailing_take_profit": row['trailing_take_profit_update']
            }
            # Append win_object to win_objects
            win_objects.append(win_object)
            # Increment trade_id
            trade_id += 1
        else:
            losses = len(results_df[results_df['trade_win'] == False])
            if row['order_type'] == "BUY_STOP":
                row_profit = (row['stop_loss'] - row['stop_price']) * row['lot_size'] * contract_size
            elif row['order_type'] == "SELL_STOP":
                row_profit = (row['stop_price'] - row['stop_loss']) * row['lot_size'] * contract_size
            profit += row_profit
            # Create a loss_object
            loss_object = {
                "trade_id": trade_id,
                "order_type": row['order_type'],
                "lot_size": row['lot_size'],
                "closing_stop_price": row['stop_price'],
                "closing_take_profit": row['take_profit'],
                "closing_stop_loss": row['stop_loss'],
                "starting_stop_loss": row['original_stop_loss'],
                "starting_take_profit": row['original_take_profit'],
                "ending_stop_loss": row['stop_loss'],
                "ending_profit_price": row['take_profit'],
                "closing_price": row['closing_price'],
                "closing_time": row['closing_time'],
                "profit": row_profit,
                "order_open_time": row['human_time'],
                "trade_open_time": row['original_start_time'],
                "trade_close_time": row['closing_time'],
                "trade_trailing_stop": row['trailing_stop_update'],
                "trade_trailing_take_profit": row['trailing_take_profit_update']
            }
            # Append loss_object to loss_objects
            loss_objects.append(loss_object)
            trade_id += 1
    # Round profit to two decimal places
    profit = round(profit, 2)
    # Create a dictionary of results
    results = {
        'total_trades': trades,
        'total_wins': wins,
        'total_losses': losses,
        'profit': profit,
        'win_objects': win_objects,
        'loss_objects': loss_objects,
        'parameters': parameters,
        'raw_strategy_candles': raw_strategy_candles,
        'proposed_trades': proposed_trades
    }

    # Return the results
    return results


# Function to calculate a grid search for a symbol
def create_grid_search(params, optimize_params=False, optimize_take_profit=False, optimize_stop_loss=False):
    # Create a list of all the possible combinations of the parameters with each element a dictionary
    # of the parameters
    if optimize_params and not optimize_take_profit and not optimize_stop_loss:
        # Create a list of all the possible combinations of the parameters with each element a dictionary
        # of the parameters
        pass
    if optimize_params and optimize_take_profit and not optimize_stop_loss:
        # Drop the first element of params which is the take profit
        params.pop(0)
        # Add a new element at the start of the params list which is a range from 0.5 to 5.0 in increments of 0.1
        params.insert(0, numpy.arange(0.5, 5.0, 0.1))
    if optimize_params and optimize_take_profit and optimize_stop_loss:
        # Remove the first element of params which is the take profit
        params.pop(0)
        # Add a new element at the start of the params list which is a range from 0.5 to 5.0 in increments of 0.1
        params.insert(0, numpy.arange(0.5, 5.0, 0.1))
        # Remove the second element of params which is the stop loss
        params.pop(1)
        # Add a new element to the second position in the params list which is a range from 0.5 to 5.0 in
        # increments of 0.1
        params.insert(1, numpy.arange(0.5, 5.0, 0.1))
    if optimize_params and not optimize_take_profit and optimize_stop_loss:
        # Remove the second element of params which is the stop loss
        params.pop(1)
        # Add a new element to the second position in the params list which is a range from 0.5 to 5.0 in increments
        # of 0.1
        params.insert(1, numpy.arange(10, 2000.0, 1))
    if not optimize_params and optimize_take_profit and not optimize_stop_loss:
        # Remove the first element of params which is the take profit
        params.pop(0)
        # Add a new element at the start of the params list which is a range from 0.5 to 5.0 in increments of 0.1
        params.insert(0, numpy.arange(0.5, 5.0, 0.1))
    if not optimize_params and optimize_take_profit and optimize_stop_loss:
        # Remove the first element of params which is the take profit
        params.pop(0)
        # Add a new element at the start of the params list which is a range from 0.5 to 5.0 in increments of 0.1
        params.insert(0, numpy.arange(0.5, 5.0, 0.1))
        # Remove the second element of params which is the stop loss
        params.pop(1)
        # Add a new element to the second position in the params list which is a range from 0.5 to 5.0 in increments
        # of 0.1
        params.insert(1, numpy.arange(0.5, 5.0, 0.1))
    if not optimize_params and not optimize_take_profit and optimize_stop_loss:
        # Remove the second element of params which is the stop loss
        params.pop(1)
        # Add a new element to the second position in the params list which is a range from 0.5 to 5.0 in increments
        # of 0.1
        params.insert(1, numpy.arange(0.5, 5.0, 0.1))
    if not optimize_params and not optimize_take_profit and not optimize_stop_loss:
        return params
    param_combinations = list(itertools.product(*params))

    # Return the list of combinations
    return param_combinations


# Function to calculate the profit or loss from a trade
def calculate_profit(row, reason, contract_size):
    # Determine if this occurred due to a stop loss or take profit
    if reason == "stop_loss":
        # Determine the order type
        if row['order_type'] == "BUY_STOP":
            # Determine if this was a profit or loss
            if row['closing_price'] > row['stop_price']:
                # This was a profit
                profit = (row['closing_price'] - row['stop_price']) * row['lot_size'] * contract_size
            else:
                # This was a loss
                profit = 0
        elif row['order_type'] == "SELL_STOP":
            # Determine if this was a profit or loss
            if row['closing_price'] < row['stop_price']:
                # This was a profit
                profit = (row['stop_price'] - row['closing_price']) * row['lot_size'] * contract_size
            else:
                # This was a loss
                profit = 0
        else:
            raise ValueError("Invalid order type")
    elif reason == "take_profit":
        # Determine the order type
        if row['order_type'] == "BUY_STOP":
            # Determine if this was a profit or loss
            if row['closing_price'] > row['stop_price']:
                # This was a profit
                profit = (row['closing_price'] - row['stop_price']) * row['lot_size'] * contract_size
            else:
                # This was a loss
                profit = 0
        elif row['order_type'] == "SELL_STOP":
            # Determine if this was a profit or loss
            if row['closing_price'] < row['stop_price']:
                # This was a profit
                profit = (row['stop_price'] - row['closing_price']) * row['lot_size'] * contract_size
            else:
                # This was a loss
                profit = 0
        else:
            raise ValueError("Invalid order type")
    else:
        raise ValueError("Invalid reason")

    # Return the profit
    return profit
