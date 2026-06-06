"""Breakout (Donchian channel) strategy.

Enters long when price breaks above the highest high of the recent lookback
window and exits when it breaks below the lowest low — the core idea behind the
classic Turtle trading system. Captures the start of strong directional moves.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.indicators import RollingExtrema
from crypto_trading_bot.models import Order, Side
from crypto_trading_bot.strategies.base import Strategy


class BreakoutStrategy(Strategy):
    """Donchian-channel breakout.

    Args:
        entry_period: Lookback for the entry (upper) channel.
        exit_period: Lookback for the exit (lower) channel.
        quantity: Base-asset quantity traded per signal.
    """

    name = "breakout"

    def __init__(
        self, entry_period: int = 20, exit_period: int = 10, quantity: float = 1.0
    ) -> None:
        if entry_period < 1 or exit_period < 1:
            raise ValueError("periods must be >= 1")
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        self.quantity = quantity
        self._entry = RollingExtrema(entry_period)
        self._exit = RollingExtrema(exit_period)
        self._holding = False

    def on_price(self, symbol: str, price: float, exchange: Exchange) -> list[Order]:
        entry_high = self._entry.high if self._entry.ready else None
        exit_low = self._exit.low if self._exit.ready else None
        # Update channels *after* reading prior values so the current bar is
        # compared against the trailing window, not against itself.
        self._entry.update(price)
        self._exit.update(price)
        base = symbol.split("/")[0]
        if not self._holding and entry_high is not None and price > entry_high:
            self._holding = True
            return [Order(symbol, Side.BUY, self.quantity, price)]
        if (
            self._holding
            and exit_low is not None
            and price < exit_low
            and exchange.balance(base) >= self.quantity
        ):
            self._holding = False
            return [Order(symbol, Side.SELL, self.quantity, price)]
        return []
