"""Tests for the momentum, mean-reversion and breakout strategies."""

from __future__ import annotations

import pytest

from crypto_trading_bot.bot import TradingBot
from crypto_trading_bot.exchanges.simulated import SimulatedExchange
from crypto_trading_bot.models import Side
from crypto_trading_bot.strategies.breakout import BreakoutStrategy
from crypto_trading_bot.strategies.mean_reversion import MeanReversionStrategy
from crypto_trading_bot.strategies.momentum import MomentumStrategy


def _ex(usdt: float = 100_000.0, btc: float = 100.0) -> SimulatedExchange:
    return SimulatedExchange(balances={"USDT": usdt, "BTC": btc}, fee_rate=0.0)


def test_momentum_validates_params() -> None:
    with pytest.raises(ValueError):
        MomentumStrategy(fast=10, slow=10)
    with pytest.raises(ValueError):
        MomentumStrategy(fast=5, slow=10, quantity=0)


def test_momentum_buys_on_golden_cross_sells_on_death_cross() -> None:
    ex = _ex()
    bot = TradingBot("BTC/USDT", MomentumStrategy(fast=3, slow=6, quantity=1.0), ex)
    # Flat warmup so both EMAs seed and align (no_was_above=True) at equality,
    # then a rise forces a golden cross (buy), then a fall forces a death cross.
    flat = [100.0] * 12
    up = [100.0 + p for p in range(1, 25)]
    down = [float(p) for p in range(124, 90, -1)]
    bot.run(flat + up + down)
    sides = [f.order.side for f in bot.fills]
    assert Side.BUY in sides
    assert Side.SELL in sides
    assert sides.index(Side.BUY) < sides.index(Side.SELL)


def test_momentum_flat_market_no_trades() -> None:
    ex = _ex()
    bot = TradingBot("BTC/USDT", MomentumStrategy(fast=3, slow=6), ex)
    bot.run([100.0] * 50)
    assert bot.fills == []


def test_mean_reversion_validates_thresholds() -> None:
    with pytest.raises(ValueError):
        MeanReversionStrategy(oversold=70, overbought=30)


def test_mean_reversion_buys_oversold_sells_overbought() -> None:
    ex = _ex()
    strat = MeanReversionStrategy(period=5, oversold=35, overbought=65, quantity=1.0)
    bot = TradingBot("BTC/USDT", strat, ex)
    # Sharp drop (oversold -> buy) then sharp rise (overbought -> sell).
    down = [float(p) for p in range(60, 20, -1)]
    up = [float(p) for p in range(20, 80)]
    bot.run(down + up)
    sides = [f.order.side for f in bot.fills]
    assert Side.BUY in sides
    assert Side.SELL in sides
    # Should not sell before buying (state machine).
    first_buy = sides.index(Side.BUY)
    assert all(s is Side.BUY for s in sides[:1]) or first_buy == 0


def test_breakout_validates_params() -> None:
    with pytest.raises(ValueError):
        BreakoutStrategy(entry_period=0)


def test_breakout_enters_on_new_high() -> None:
    ex = _ex()
    strat = BreakoutStrategy(entry_period=5, exit_period=3, quantity=1.0)
    bot = TradingBot("BTC/USDT", strat, ex)
    # Flat then a clear breakout up, then a breakdown.
    prices = [100.0] * 6 + [101, 102, 103, 104, 105] + [95, 90, 85]
    bot.run([float(p) for p in prices])
    sides = [f.order.side for f in bot.fills]
    assert Side.BUY in sides
    assert Side.SELL in sides


def test_breakout_no_entry_without_breakout() -> None:
    ex = _ex()
    strat = BreakoutStrategy(entry_period=5, exit_period=3)
    bot = TradingBot("BTC/USDT", strat, ex)
    bot.run([100.0] * 30)  # never exceeds the channel high
    assert bot.fills == []
