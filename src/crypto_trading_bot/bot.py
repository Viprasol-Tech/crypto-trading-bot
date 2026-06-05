"""The bot runner: feed prices to a strategy and execute its orders.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from collections.abc import Sequence

from crypto_trading_bot.exchanges.simulated import SimulatedExchange
from crypto_trading_bot.models import Fill
from crypto_trading_bot.strategies.base import Strategy


class TradingBot:
    """Drive one strategy on one symbol against a simulated exchange."""

    def __init__(self, symbol: str, strategy: Strategy, exchange: SimulatedExchange) -> None:
        self.symbol = symbol
        self.strategy = strategy
        self.exchange = exchange
        self.fills: list[Fill] = []

    def on_price(self, price: float) -> None:
        """Process one price update."""
        self.exchange.set_price(self.symbol, price)
        for order in self.strategy.on_price(self.symbol, price, self.exchange):
            self.fills.append(self.exchange.execute(order))

    def run(self, prices: Sequence[float]) -> float:
        """Replay a price series and return final equity (quote currency)."""
        for price in prices:
            self.on_price(price)
        return self.exchange.equity()
