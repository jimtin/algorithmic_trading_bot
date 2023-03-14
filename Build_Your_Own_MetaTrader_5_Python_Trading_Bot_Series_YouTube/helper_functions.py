

# Function to calculate FOREX lot size on MT5
def calc_lot_size(balance, risk_amount, stop_loss, stop_price, symbol):
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
    # Calculate the amount to risk
    amount_to_risk = balance * risk_amount

    # Make sure symbol has any denotation of raw removed
    symbol_name = symbol.split(".")
    symbol_name = symbol_name[0]

    # Branch based on lot size
    if symbol == "USDJPY":
        # USDJPY pip size is 0.01
        pip_size = 0.01
        # Calculate the amount of pips being risked
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        # Calculate the pip value
        pip_value = amount_to_risk / stop_pips_integer
        # Add in the exchange rate as the USD is the counter currency
        pip_value = pip_value * stop_price #<- we can use the current exchange rate in the stop price
        # Calculate the raw lot_size
        raw_lot_size = pip_value / 1000
    # Add in another counter currency example
    elif symbol == "USDCAD":
        # Pip size is 0.0001
        pip_size = 0.0001
        # Calculate the amount of pips being risked
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        # Calculate the pip value
        pip_value = amount_to_risk / stop_pips_integer
        # Add in the exchange rate
        pip_value = pip_value * stop_price
        # Calculate the raw lot size
        raw_lot_size = pip_value / 10
    else:
        # Standard calculation, no need for exchange rate
        pip_size = 0.0001
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

