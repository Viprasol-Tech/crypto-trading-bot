"""Strategy interface for the crypto trading bot.

A strategy reacts to a new price and returns the orders it wants to place. The
runner executes them on the exchange. Keeping strategies pure (price in, orders
out) makes them trivial to unit-test and backtest.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.models import Order


class Strategy(ABC):
    """Base class for crypto trading strategies."""

    name: str = "strategy"

    @abstractmethod
    def on_price(self, symbol: str, price: float, exchange: Exchange) -> list[Order]:
        """Return orders to place given the latest price."""
        raise NotImplementedError
