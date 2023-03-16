import multiprocessing

from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import indicator_lib
import talib
import mt5_lib
import pandas
from multiprocessing import Queue
from multiprocessing import Process
from threading import Thread
import os


# Function to multi-optimize a strategy
def multi_optimize(strategy, cash, commission, symbols, timeframes, exchange):
    """
    Function to run a backtest optimizing across symbols, timeframes
    :param strategy: string of the strategy to be tested
    :param cash: integer of the cash to start with
    :param commission: decimal value of the percentage commission fees
    :param symbol: string of the symbol to be tested
    :param timeframe: string of the timeframe to be tested
    :param params: json dict of the parameters to be passed to the strategy
    :return:
    """
    # Todo: add in args to support different strategies which may need different optimization parameters
    # Todo: Change the data gathering so that it supports getting a time range of data instead of a number of candles
    # Todo: Add in support for FOREX
    # Todo: Add in support for crypto
    # Todo: Add in support for other exchanges
    # Todo: Add in lot size support
    # Todo: Add in support for using custom indicators
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
                data = mt5_lib.query_historic_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    number_of_candles=10000
                )
                # Get current working directory
                save_location = os.path.abspath(os.getcwd())
                # Create the save path
                plot_save_path = f"{save_location}" + "/plots/" + f"{strategy}" + "_" + f"{exchange}" + "_" + f"{symbol}" + "_" + f"{timeframe}" + "_" + f"{cash}" + "_" + f"{commission}" + "_" + ".html"
                result_save_path = f"{save_location}" + "/results/" + f"{strategy}" + "_" + f"{exchange}" + "_" + f"{symbol}" + "_" + f"{timeframe}" + "_" + f"{cash}" + "_" + f"{commission}" + "_" + ".json"
                # Create tuple
                args_tuple = (data, strategy, cash, commission, True, True, plot_save_path, result_save_path, symbol, timeframe, exchange)
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


def run_backtest(data, strategy, cash, commission, optimize=False, save=False, plot_save_location=None, result_save_location=None, symbol=None, timeframe=None, exchange=None):
    """
    Function to run a backtest
    :param data: raw dataframe to use for backtesting
    :param Strategy: Strategy to use for backtesting
    :param cash: Start cash
    :param commission: Commission fees (percentage expressed as decimal)
    :return: backtest outcomes
    """
    print("Processing")
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
        strategy = EMACross
    # Initialize the backtest
    backtest = Backtest(data, strategy, cash=cash, commission=commission)
    # If optimize is true, optimize the strategy
    if optimize:
        # Optimize the strategy
        stats = backtest.optimize(
            n1=range(5, 50, 1),
            n2=range(50, 200, 1),
            maximize='Equity Final [$]',
            constraint=lambda p: p.n1 < p.n2
        )
    else:
        # Run the backtest
        stats = backtest.run()
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
    if save:
        stats.to_json(result_save_location)

    return stats


class EMACross(Strategy):
    n1 = 20
    n2 = 50

    def init(self):
        self.ema_1 = self.I(talib.EMA, self.data.Close, self.n1)
        self.ema_2 = self.I(talib.EMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.ema_1, self.ema_2):
            self.position.close()
            self.buy()
        elif crossover(self.ema_2, self.ema_1):
            self.position.close()
            self.sell()

