"""Grid trading strategy.

Places a ladder of buy levels below a reference price and sells a slice each time
price climbs back through a level — profiting from range-bound chop. A classic,
fully mechanical crypto strategy.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.models import Order, Side
from crypto_trading_bot.strategies.base import Strategy


class GridStrategy(Strategy):
    """Buy the dips on a fixed price grid, sell into strength.

    Args:
        lower: Bottom of the grid.
        upper: Top of the grid.
        levels: Number of grid lines.
        quantity: Base-asset quantity traded per level.
    """

    name = "grid"

    def __init__(self, lower: float, upper: float, levels: int, quantity: float) -> None:
        if lower <= 0 or upper <= lower or levels < 2:
            raise ValueError("require 0 < lower < upper and levels >= 2")
        self.lower = lower
        self.upper = upper
        self.levels = levels
        self.quantity = quantity
        self.step = (upper - lower) / (levels - 1)
        self._last_index: int | None = None

    def _index_for(self, price: float) -> int:
        clamped = min(max(price, self.lower), self.upper)
        return round((clamped - self.lower) / self.step)

    def on_price(self, symbol: str, price: float, exchange: Exchange) -> list[Order]:
        index = self._index_for(price)
        if self._last_index is None:
            self._last_index = index
            return []
        orders: list[Order] = []
        if index < self._last_index:
            # Price dropped through one or more levels -> buy.
            orders.append(Order(symbol, Side.BUY, self.quantity, price))
        elif index > self._last_index:
            # Price rose through one or more levels -> sell (if we hold enough).
            base = symbol.split("/")[0]
            if exchange.balance(base) >= self.quantity:
                orders.append(Order(symbol, Side.SELL, self.quantity, price))
        self._last_index = index
        return orders
