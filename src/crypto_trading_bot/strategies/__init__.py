"""Trading strategies: grid, DCA, momentum, mean-reversion and breakout."""

from __future__ import annotations

from crypto_trading_bot.strategies.base import Strategy
from crypto_trading_bot.strategies.breakout import BreakoutStrategy
from crypto_trading_bot.strategies.dca import DCAStrategy
from crypto_trading_bot.strategies.grid import GridStrategy
from crypto_trading_bot.strategies.mean_reversion import MeanReversionStrategy
from crypto_trading_bot.strategies.momentum import MomentumStrategy

__all__ = [
    "BreakoutStrategy",
    "DCAStrategy",
    "GridStrategy",
    "MeanReversionStrategy",
    "MomentumStrategy",
    "Strategy",
]
