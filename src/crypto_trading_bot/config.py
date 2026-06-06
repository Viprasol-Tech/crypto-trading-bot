"""Pydantic configuration models and the strategy registry.

``BotConfig`` validates a full run (symbol, cash, cost model, chosen strategy and
its params) and can build the strategy instance. The registry maps strategy
names to classes so the CLI and config share one source of truth.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from crypto_trading_bot.fees import CostModel
from crypto_trading_bot.strategies.base import Strategy
from crypto_trading_bot.strategies.breakout import BreakoutStrategy
from crypto_trading_bot.strategies.dca import DCAStrategy
from crypto_trading_bot.strategies.grid import GridStrategy
from crypto_trading_bot.strategies.mean_reversion import MeanReversionStrategy
from crypto_trading_bot.strategies.momentum import MomentumStrategy

STRATEGY_REGISTRY: dict[str, type[Strategy]] = {
    "grid": GridStrategy,
    "dca": DCAStrategy,
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
    "breakout": BreakoutStrategy,
}

#: Sensible default parameters per strategy, used by the CLI demo.
DEFAULT_PARAMS: dict[str, dict[str, Any]] = {
    "grid": {"lower": 85.0, "upper": 115.0, "levels": 13, "quantity": 1.0},
    "dca": {"quote_amount": 100.0, "interval": 5},
    "momentum": {"fast": 12, "slow": 26, "quantity": 1.0},
    "mean_reversion": {"period": 14, "oversold": 30.0, "overbought": 70.0, "quantity": 1.0},
    "breakout": {"entry_period": 20, "exit_period": 10, "quantity": 1.0},
}


def available_strategies() -> list[str]:
    """Names of all registered strategies, sorted."""
    return sorted(STRATEGY_REGISTRY)


def build_strategy(name: str, params: dict[str, Any] | None = None) -> Strategy:
    """Instantiate a strategy by name with optional parameter overrides."""
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"unknown strategy {name!r}; choose from {available_strategies()}")
    merged = {**DEFAULT_PARAMS.get(name, {}), **(params or {})}
    return STRATEGY_REGISTRY[name](**merged)


class CostConfig(BaseModel):
    """Cost-model configuration."""

    fee_rate: float = Field(default=0.001, ge=0.0)
    slippage_bps: float = Field(default=0.0, ge=0.0)

    def to_model(self) -> CostModel:
        return CostModel(fee_rate=self.fee_rate, slippage_bps=self.slippage_bps)


class BotConfig(BaseModel):
    """A validated, self-contained description of a backtest/run."""

    symbol: str = "BTC/USDT"
    cash: float = Field(default=10_000.0, gt=0.0)
    strategy: str = "grid"
    params: dict[str, Any] = Field(default_factory=dict)
    costs: CostConfig = Field(default_factory=CostConfig)

    @field_validator("symbol")
    @classmethod
    def _check_symbol(cls, value: str) -> str:
        if value.count("/") != 1 or any(not part for part in value.split("/")):
            raise ValueError("symbol must look like 'BASE/QUOTE', e.g. 'BTC/USDT'")
        return value

    @field_validator("strategy")
    @classmethod
    def _check_strategy(cls, value: str) -> str:
        if value not in STRATEGY_REGISTRY:
            raise ValueError(f"unknown strategy {value!r}; choose from {available_strategies()}")
        return value

    def build(self) -> Strategy:
        """Build the configured strategy instance."""
        return build_strategy(self.strategy, self.params)
