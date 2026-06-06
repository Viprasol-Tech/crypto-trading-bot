"""Tests for the cost model and the upgraded simulated exchange."""

from __future__ import annotations

import math

import pytest

from crypto_trading_bot.exchanges.simulated import InsufficientFunds, SimulatedExchange
from crypto_trading_bot.fees import CostModel
from crypto_trading_bot.models import Order, Side


def test_cost_model_rejects_negative() -> None:
    with pytest.raises(ValueError):
        CostModel(fee_rate=-0.1)
    with pytest.raises(ValueError):
        CostModel(slippage_bps=-1)


def test_slippage_moves_against_the_trader() -> None:
    cm = CostModel(slippage_bps=10)  # 0.10%
    assert math.isclose(cm.fill_price(Side.BUY, 100.0), 100.1)
    assert math.isclose(cm.fill_price(Side.SELL, 100.0), 99.9)


def test_fee_is_proportional_to_notional() -> None:
    cm = CostModel(fee_rate=0.001)
    assert math.isclose(cm.fee(1000.0), 1.0)


def test_exchange_applies_fee_and_slippage() -> None:
    cm = CostModel(fee_rate=0.001, slippage_bps=50)  # 0.5% slippage
    ex = SimulatedExchange(balances={"USDT": 10_000.0}, cost_model=cm)
    ex.set_price("BTC/USDT", 100.0)
    fill = ex.execute(Order("BTC/USDT", Side.BUY, 1.0, 100.0))
    assert math.isclose(fill.executed_price, 100.5)  # paid more
    assert fill.fee > 0
    # cash spent = 100.5 + fee
    assert math.isclose(ex.balance("USDT"), 10_000.0 - 100.5 - fill.fee)
    assert math.isclose(ex.balance("BTC"), 1.0)


def test_exchange_blocks_unaffordable_buy() -> None:
    ex = SimulatedExchange(balances={"USDT": 50.0}, fee_rate=0.0)
    ex.set_price("BTC/USDT", 100.0)
    with pytest.raises(InsufficientFunds):
        ex.execute(Order("BTC/USDT", Side.BUY, 1.0, 100.0))


def test_exchange_blocks_oversell() -> None:
    ex = SimulatedExchange(balances={"USDT": 0.0, "BTC": 0.5}, fee_rate=0.0)
    ex.set_price("BTC/USDT", 100.0)
    with pytest.raises(InsufficientFunds):
        ex.execute(Order("BTC/USDT", Side.SELL, 1.0, 100.0))


def test_allow_short_permits_negative_balances() -> None:
    ex = SimulatedExchange(balances={"USDT": 0.0}, fee_rate=0.0, allow_short=True)
    ex.set_price("BTC/USDT", 100.0)
    fill = ex.execute(Order("BTC/USDT", Side.BUY, 1.0, 100.0))
    assert fill is not None
    assert ex.balance("USDT") < 0


def test_fill_notional_and_executed_price_defaults() -> None:
    ex = SimulatedExchange(balances={"USDT": 1_000.0}, fee_rate=0.0)
    ex.set_price("BTC/USDT", 100.0)
    fill = ex.execute(Order("BTC/USDT", Side.BUY, 2.0, 100.0))
    assert math.isclose(fill.notional, 200.0)
    assert math.isclose(fill.executed_price, 100.0)
