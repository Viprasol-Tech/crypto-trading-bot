"""The bot runner: feed prices to a strategy and execute its orders.

Tracks fills, an equity curve and a :class:`~crypto_trading_bot.portfolio.Portfolio`
so live/paper runs report the same metrics as a backtest. Orders that cannot be
afforded are skipped (logged via the returned ``rejected`` counter).

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from collections.abc import Sequence

from crypto_trading_bot.exchanges.simulated import InsufficientFunds, SimulatedExchange
from crypto_trading_bot.models import Fill
from crypto_trading_bot.portfolio import Portfolio
from crypto_trading_bot.strategies.base import Strategy


class TradingBot:
    """Drive one strategy on one symbol against a simulated exchange."""

    def __init__(self, symbol: str, strategy: Strategy, exchange: SimulatedExchange) -> None:
        self.symbol = symbol
        self.strategy = strategy
        self.exchange = exchange
        self.fills: list[Fill] = []
        self.rejected = 0
        self.equity_curve: list[float] = []
        quote = symbol.split("/")[1]
        self.portfolio = Portfolio(cash=exchange.balance(quote), quote=quote)

    def on_price(self, price: float) -> None:
        """Process one price update."""
        self.exchange.set_price(self.symbol, price)
        for order in self.strategy.on_price(self.symbol, price, self.exchange):
            try:
                fill = self.exchange.execute(order)
            except InsufficientFunds:
                self.rejected += 1
                continue
            self.fills.append(fill)
            self.portfolio.apply(fill)
        self.equity_curve.append(self.exchange.equity(self.symbol.split("/")[1]))

    def run(self, prices: Sequence[float]) -> float:
        """Replay a price series and return final equity (quote currency)."""
        for price in prices:
            self.on_price(price)
        return self.exchange.equity(self.symbol.split("/")[1])
