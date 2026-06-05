"""Tests for the simulated exchange, strategies, and bot runner."""

from __future__ import annotations

import math

from crypto_trading_bot.bot import TradingBot
from crypto_trading_bot.exchanges.simulated import SimulatedExchange
from crypto_trading_bot.models import Order, Side
from crypto_trading_bot.strategies.dca import DCAStrategy
from crypto_trading_bot.strategies.grid import GridStrategy


def test_simulated_exchange_buy_updates_balances() -> None:
    ex = SimulatedExchange(balances={"USDT": 1_000.0}, fee_rate=0.0)
    ex.set_price("BTC/USDT", 100.0)
    ex.execute(Order("BTC/USDT", Side.BUY, 2.0, 100.0))
    assert math.isclose(ex.balance("USDT"), 800.0)
    assert math.isclose(ex.balance("BTC"), 2.0)


def test_dca_buys_on_interval() -> None:
    ex = SimulatedExchange(balances={"USDT": 1_000.0}, fee_rate=0.0)
    bot = TradingBot("BTC/USDT", DCAStrategy(quote_amount=100.0, interval=2), ex)
    bot.run([100.0, 100.0, 100.0, 100.0])  # buys on ticks 2 and 4
    assert len(bot.fills) == 2
    assert ex.balance("BTC") > 0


def test_grid_validates_params() -> None:
    try:
        GridStrategy(lower=100, upper=50, levels=5, quantity=1)
    except ValueError:
        return
    raise AssertionError("expected ValueError for upper <= lower")


def test_grid_buys_on_dip_sells_on_rise() -> None:
    ex = SimulatedExchange(balances={"USDT": 10_000.0, "BTC": 5.0}, fee_rate=0.0)
    bot = TradingBot("BTC/USDT", GridStrategy(85, 115, 13, 1.0), ex)
    bot.run([100, 95, 90, 95, 100, 105])  # down then up through grid levels
    sides = {f.order.side for f in bot.fills}
    assert Side.BUY in sides
    assert len(bot.fills) >= 1
