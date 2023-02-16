import mt5_lib
from tradecalc import tradecalc


# Function to make a trade
def make_trade(balance, comment, amount_to_risk, symbol, take_profit, stop_loss, stop_price):
    """
    Function to make a trade once a price signal is retrieved.
    :param balance: float of current balance / or static balance
    :param amount_to_risk: float of the amount to risk (expressed as decimal)
    :param take_profit: float of take_profit price
    :param stop_loss: float of stop_loss price
    :param stop_price: float of stop_price
    :param symbol: string of the symbol being traded
    :return: trade_outcome
    """
    # Format all values
    balance = float(balance)
    balance = round(balance, 2)
    take_profit = float(take_profit)
    take_profit = round(take_profit, 4)
    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, 4)
    stop_price = float(stop_price)
    stop_price = round(stop_price, 4)

    # Pseudo code
    # 1. Determine lot size
    lot_size = calc_lot_size(
        balance=balance,
        risk_amount=amount_to_risk,
        stop_loss=stop_loss,
        stop_price=stop_price,
        symbol=symbol
    )
    # 2. Send trade to MT5
    # Determine trade type
    if stop_price > stop_loss:
        trade_type = "BUY_STOP"
    else:
        trade_type = "SELL_STOP"
    # Send to MT5
    trade_outcome = mt5_lib.place_order(
        order_type=trade_type,
        symbol=symbol,
        volume=lot_size,
        stop_loss=stop_loss,
        stop_price=stop_price,
        take_profit=take_profit,
        comment=comment,
        direct=False
    )
    # Return the trade outcome to user
    return trade_outcome


# Function to calculate lot size
def calc_lot_size(balance, risk_amount, stop_loss, stop_price, symbol):
    """
    Function to calculate the lot size for a trade. The balance in this case is static, but can be easily modified to
    be dynamic by querying the account of your MT5 broker
    :param balance: float of the balance being risked
    :param risk_amount: float of the amount to risk
    :param stop_loss: float of the stop_loss
    :param stop_price: float of the stop_price
    :param symbol: string of the symbol
    :return: float of the lot_size
    """
    # Calculate the amount to risk
    amount_to_risk = balance * risk_amount

    # Determine lot size based on symbol
    if symbol == "USDJPY.a": #<- This may need to be changed depending on your broker
        # USDJPY pip size is 0.01
        pip_size = 0.01
        # Calculate the amount of pips being risked
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        # Calculate the pip value
        pip_value = amount_to_risk / stop_pips_integer
        # Add in the exchange rate as USD is the counter currency
        pip_value = pip_value * stop_price
        # Calculate the raw lot_size
        raw_lot_size = pip_value / 1000
    elif symbol == "BTCUSD.a":
        # Use the tradecalc library to calculate risk
        risk = tradecalc.get_risk_per_unit(price=stop_price, sl_price=stop_loss)
        raw_lot_size = tradecalc.get_position_size(insert=amount_to_risk, risk_per_unit=risk)
    elif symbol == "USDCAD.a": # <- Including another counter currency example
        # Pip size is typically 0.0001
        pip_size = 0.0001
        # Calculate the amount of pips being risked
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        # Calculate the pip value
        pip_value = amount_to_risk / stop_pips_integer
        # Calculate the raw lot size
        raw_lot_size = pip_value / 10
    else: # <- Make sure you check your own currency!
        # Pip size is typically 0.0001
        pip_size = 0.0001
        # Calculate the amount of pips being risked
        stop_pips_integer = abs((stop_price - stop_loss)/pip_size)
        # Calculate the pip value
        pip_value = amount_to_risk / stop_pips_integer
        # Calculate the raw lot size
        raw_lot_size = pip_value / 10

    # Format lot size to be MT5 friendly. This may change depending on your broker
    lot_size = float(raw_lot_size)
    lot_size = round(lot_size, 2)
    # Include a quick catch to make sure lot size doesn't go crazy.
    if lot_size >= 10:
        lot_size = 9.99
    return lot_size


