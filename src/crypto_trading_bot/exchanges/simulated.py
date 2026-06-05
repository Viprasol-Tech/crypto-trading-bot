"""A simulated exchange for paper trading and backtests.

Holds balances per asset and fills orders instantly at the current price (set by
the caller or a price feed). Symbols are ``BASE/QUOTE`` (e.g. ``BTC/USDT``).

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.models import Fill, Order, Side


class SimulatedExchange(Exchange):
    """In-memory exchange with configurable fees and balances."""

    def __init__(self, balances: dict[str, float] | None = None, fee_rate: float = 0.001) -> None:
        self._balances: dict[str, float] = dict(balances or {})
        self._prices: dict[str, float] = {}
        self.fee_rate = fee_rate

    def set_price(self, symbol: str, price: float) -> None:
        """Update the current price used for fills/quotes."""
        self._prices[symbol] = price

    def price(self, symbol: str) -> float:
        return self._prices.get(symbol, 0.0)

    def balance(self, asset: str) -> float:
        return self._balances.get(asset, 0.0)

    def execute(self, order: Order) -> Fill:
        base, quote = order.symbol.split("/")
        notional = order.price * order.quantity
        fee = notional * self.fee_rate
        if order.side is Side.BUY:
            self._balances[quote] = self.balance(quote) - notional - fee
            self._balances[base] = self.balance(base) + order.quantity
        else:
            self._balances[base] = self.balance(base) - order.quantity
            self._balances[quote] = self.balance(quote) + notional - fee
        return Fill(order=order, fee=fee)

    def equity(self, quote: str = "USDT") -> float:
        """Total equity valued in the quote asset at current prices."""
        total = self.balance(quote)
        for symbol, price in self._prices.items():
            base = symbol.split("/")[0]
            total += self.balance(base) * price
        return total
