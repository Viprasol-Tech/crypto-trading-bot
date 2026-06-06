"""Crypto Trading Bot - multi-exchange crypto bot by Viprasol Tech.

Public API re-exports the most-used building blocks so callers can write
``from crypto_trading_bot import run_backtest, MomentumStrategy`` directly.
"""

from __future__ import annotations

from crypto_trading_bot.backtest import BacktestReport, run_backtest
from crypto_trading_bot.bot import TradingBot
from crypto_trading_bot.config import (
    BotConfig,
    available_strategies,
    build_strategy,
)
from crypto_trading_bot.exchanges.simulated import InsufficientFunds, SimulatedExchange
from crypto_trading_bot.fees import CostModel
from crypto_trading_bot.models import Fill, Order, Side
from crypto_trading_bot.portfolio import Portfolio, PortfolioSnapshot, Position
from crypto_trading_bot.strategies.base import Strategy
from crypto_trading_bot.strategies.breakout import BreakoutStrategy
from crypto_trading_bot.strategies.dca import DCAStrategy
from crypto_trading_bot.strategies.grid import GridStrategy
from crypto_trading_bot.strategies.mean_reversion import MeanReversionStrategy
from crypto_trading_bot.strategies.momentum import MomentumStrategy

__version__ = "0.2.0"
__author__ = "Viprasol Tech Private Limited"
__all__ = [
    "BacktestReport",
    "BotConfig",
    "BreakoutStrategy",
    "CostModel",
    "DCAStrategy",
    "Fill",
    "GridStrategy",
    "InsufficientFunds",
    "MeanReversionStrategy",
    "MomentumStrategy",
    "Order",
    "Portfolio",
    "PortfolioSnapshot",
    "Position",
    "Side",
    "SimulatedExchange",
    "Strategy",
    "TradingBot",
    "__version__",
    "available_strategies",
    "build_strategy",
    "run_backtest",
]
