from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import talib


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

