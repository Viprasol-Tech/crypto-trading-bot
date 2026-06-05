"""Exchange interface.

Implement this to connect a real exchange (Binance, Coinbase, Kraken, …). The
bundled :class:`~crypto_trading_bot.exchanges.simulated.SimulatedExchange` lets
you run and backtest strategies without real funds or API keys.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from crypto_trading_bot.models import Fill, Order


class Exchange(ABC):
    """Abstract crypto exchange."""

    @abstractmethod
    def price(self, symbol: str) -> float:
        """Return the current price for a symbol."""

    @abstractmethod
    def execute(self, order: Order) -> Fill:
        """Execute an order and return the resulting fill."""

    @abstractmethod
    def balance(self, asset: str) -> float:
        """Return the free balance of an asset (e.g. 'USDT', 'BTC')."""
