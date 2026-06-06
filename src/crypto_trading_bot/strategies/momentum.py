"""Momentum (dual EMA crossover) strategy.

Goes long when a fast EMA crosses above a slow EMA (uptrend) and exits the
position when it crosses back below — a classic trend-following approach that
rides sustained moves and sidesteps chop better than a single moving average.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.indicators import EMA
from crypto_trading_bot.models import Order, Side
from crypto_trading_bot.strategies.base import Strategy


class MomentumStrategy(Strategy):
    """Trend-following dual-EMA crossover.

    Args:
        fast: Fast EMA period.
        slow: Slow EMA period (must be greater than ``fast``).
        quantity: Base-asset quantity traded per signal.
    """

    name = "momentum"

    def __init__(self, fast: int = 12, slow: int = 26, quantity: float = 1.0) -> None:
        if fast < 1 or slow <= fast:
            raise ValueError("require 1 <= fast < slow")
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        self.quantity = quantity
        self._fast = EMA(fast)
        self._slow = EMA(slow)
        self._was_above: bool | None = None

    def on_price(self, symbol: str, price: float, exchange: Exchange) -> list[Order]:
        fast = self._fast.update(price)
        slow = self._slow.update(price)
        if fast is None or slow is None:
            return []
        is_above = fast > slow
        if self._was_above is None:
            self._was_above = is_above
            return []
        orders: list[Order] = []
        base = symbol.split("/")[0]
        if is_above and not self._was_above:
            # Golden cross -> enter long.
            orders.append(Order(symbol, Side.BUY, self.quantity, price))
        elif not is_above and self._was_above and exchange.balance(base) >= self.quantity:
            # Death cross -> exit long.
            orders.append(Order(symbol, Side.SELL, self.quantity, price))
        self._was_above = is_above
        return orders
