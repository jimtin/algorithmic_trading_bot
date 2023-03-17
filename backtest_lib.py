import multiprocessing

from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import indicator_lib
import talib
import mt5_lib
import pandas
import os
import helper_functions


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
            strategy = EMACross
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


class EMACross(Strategy):
    n1 = 20
    n2 = 50
    forex = False

    def init(self):
        #print(f"Testing EMA Cross Strategy with Parameters: N1 = {self.n1}, N2 = {self.n2}")
        self.ema_1 = self.I(talib.EMA, self.data.Close, self.n1)
        self.ema_2 = self.I(talib.EMA, self.data.Close, self.n2)

    def next(self):

        if crossover(self.ema_1, self.ema_2):
            # Close any open positions
            self.position.close()
            # Create a buy order
            self.order_create("BUY")
        elif crossover(self.ema_2, self.ema_1):
            # Close open positions
            self.position.close()
            # Create the order
            self.order_create("SELL")

    def order_create(self, order_type):
        if order_type == "BUY":
            # Create a stop price for the order at 1% above the previous close
            stop_price = self.data.Low[-1] * 1.01
            # Create a stop_loss price for the order at 5% below the previous close
            stop_loss = self.data.Close[-1] * 0.9
            self.buy(sl=stop_loss, limit=stop_price, volume=0.01)
        elif order_type == "SELL":
            # Create a stop price for the order at 1% below the previous close
            stop_price = self.data.Close[-1] * 0.99
            # Create a stop_loss price for the order at 5% above the previous close
            stop_loss = self.data.Low[-1] * 1.1
            self.sell(sl=stop_loss, limit=stop_price)
