"""Dollar-Cost Averaging (DCA) strategy.

Buys a fixed quote amount (e.g. $50) every N price updates, regardless of price —
the simplest, most popular crypto accumulation strategy.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.models import Order, Side
from crypto_trading_bot.strategies.base import Strategy


class DCAStrategy(Strategy):
    """Buy a fixed quote-amount on a fixed cadence.

    Args:
        quote_amount: Amount of quote currency to spend each interval.
        interval: Number of price updates between buys.
    """

    name = "dca"

    def __init__(self, quote_amount: float, interval: int = 1) -> None:
        if quote_amount <= 0 or interval < 1:
            raise ValueError("quote_amount must be > 0 and interval >= 1")
        self.quote_amount = quote_amount
        self.interval = interval
        self._tick = 0

    def on_price(self, symbol: str, price: float, exchange: Exchange) -> list[Order]:
        self._tick += 1
        if price <= 0 or self._tick % self.interval != 0:
            return []
        quantity = self.quote_amount / price
        return [Order(symbol, Side.BUY, quantity, price)]
