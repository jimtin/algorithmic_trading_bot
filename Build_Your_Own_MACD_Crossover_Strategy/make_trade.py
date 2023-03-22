import mt5_lib
import helper_functions


# Function to make a trade
def make_trade(balance, comment, amount_to_risk, symbol, take_profit, stop_loss, stop_price):
    """
    Function to make a trade once a price signal is retrieved
    :param balance: float of current balance / static balance
    :param comment: string of comment. Used to denote different strategies in same account.
    :param amount_to_risk: float (decimal) of amount to risk from balance
    :param symbol: string of the symbol being traded
    :param take_profit: float of the take_profit price
    :param stop_loss: float of the stop_loss price
    :param stop_price: float of the stop_price
    :return: trade outcome
    """
    ### Pseudo Code:
    # 1. Format all values
    # 2. Determine the lot size
    # 3. Send trade to MT5
    # 4. Return outcome
    # Future: Send trade outcome / signal to Discord
    # Future: Account for different currency in balance (i.e. AUD to USD when trading USDJPY)

    # todo: Add in a balance converter here

    # Format values
    balance = float(balance)
    balance = round(balance, 2)
    take_profit = float(take_profit)
    take_profit = round(take_profit, 4)
    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, 4)
    stop_price = float(stop_price)
    stop_price = round(stop_price, 4)

    # 2. Get Lot Size
    lot_size = helper_functions.calc_lot_size(
        balance=balance,
        risk_amount=amount_to_risk,
        stop_loss=stop_loss,
        stop_price=stop_price,
        symbol=symbol
    )

    # 3. Send trade to MT5
    # Determine trade type
    if stop_price > stop_loss:
        trade_type = "BUY_STOP"
    else:
        trade_type = "SELL_STOP"

    # 3: Send trade to MT5 pt 2
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

    # todo: Send to Discord here

    # 4: Return Outcome
    return trade_outcome


