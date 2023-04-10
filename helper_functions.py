import mt5_lib
import binance_lib


# Function to calculate FOREX lot size on MT5
def calc_lot_size(balance, risk_amount, stop_loss, stop_price, symbol, exchange="mt5", my_currency="USD", pip_size=None, base_currency=None):
    """
    Function to calculate a lot size (or volume) for a FOREX trade on MT5. The balance is passed as a static amount,
    any compounding is taken care of in the parent function.
    :param balance: float of the balance being risked
    :param risk_amount: float of the amount to risk
    :param stop_loss: float of the stop_loss
    :param stop_price: float of the stop_price
    :param symbol: string of the symbol
    :return: float of the lot_size
    """
    # Make sure symbol has any denotation of raw removed
    symbol_name = symbol.split(".")
    symbol_name = symbol_name[0]

    # Get USD equivalent of balance
    if my_currency == "USD":
        pass
    else:
        # Get the exchange rate
        exchange_rate = mt5_lib.get_exchange_rate(symbol=my_currency + "USD")
        balance = balance * exchange_rate

    # Calculate the amount to risk
    amount_to_risk = balance * risk_amount

    # Raise an error if pip_size is not None and base_currency is None
    if pip_size is not None and base_currency is None:
        raise ValueError("If pip_size is not None, base_currency must also be specified")

    # Get the pip size
    if pip_size is None:
        if exchange == "mt5":
            pip_size = mt5_lib.get_pip_size(symbol=symbol)
            base_currency = mt5_lib.get_base_currency(symbol=symbol)
        else:
            raise ValueError("Exchange not supported")
    # Branch based on profit currency
    if base_currency == "USD":
        # Calculate the amount of pips being risked
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        # Calculate the pip value
        pip_value = amount_to_risk / stop_pips_integer
        if symbol_name == "USDJPY":
            # Calculate the raw lot_size
            raw_lot_size = pip_value / 1000
        elif symbol_name == "ETHUSD":
            # Calculate the raw lot_size
            raw_lot_size = pip_value * 100
        else:
            raw_lot_size = pip_value / 10
    else:
        # Calculate number of pips being risked
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        # Calculate the pip value
        pip_value = amount_to_risk / stop_pips_integer
        # Calculate the raw lot size
        raw_lot_size = pip_value / 10

    # Format lot size to be MT5 friendly. This may change based on your broker (i.e. if they do micro lots etc)
    # Turn into a float
    lot_size = float(raw_lot_size)
    # Round to 2 decimal places. NOTE: If you have a small balance (< 5000 USD) this rounding may impact risk
    lot_size = round(lot_size, 2)
    # Add in a quick catch to make sure lot size isn't extreme. You can modify this
    if lot_size >= 10:
        lot_size = 9.99
    return lot_size

# Get Data function
# todo: Update this accept a timerange
def get_data(symbol, timeframe, exchange="mt5", ):
    """
    Function to retrieve data from supported exchanges. Data is in the form of candlesticks and should be returned as a
    dataframe
    :param symbol: string of the symbol to be retrieved
    :param timeframe: string of the timeframe to be queried
    :param exchange: string of the exchange to be queried. Default "mt5"
    :return: dataframe
    """
    if exchange == "mt5":
        # Get the data
        data = mt5_lib.get_candlesticks(symbol=symbol, timeframe=timeframe, number_of_candles=1000)
    elif exchange == "binance":
        # Get the data
        data = binance_lib.get_candlesticks(symbol=symbol, timeframe=timeframe, number_of_candles=1000)
    # If unsupported exchange queried, raise an error
    else:
        raise ValueError("Exchange not supported")
    # Return the data
    return data
