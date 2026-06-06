"""Tests for the portfolio tracker."""

from __future__ import annotations

import math

from crypto_trading_bot.models import Fill, Order, Side
from crypto_trading_bot.portfolio import Portfolio, PortfolioSnapshot


def _fill(side: Side, qty: float, price: float, fee: float = 0.0) -> Fill:
    return Fill(order=Order("BTC/USDT", side, qty, price), fee=fee, fill_price=price)


def test_buy_updates_cash_and_avg_price() -> None:
    pf = Portfolio(cash=1_000.0)
    pf.apply(_fill(Side.BUY, 2.0, 100.0))
    assert math.isclose(pf.cash, 800.0)
    assert math.isclose(pf.positions["BTC"].quantity, 2.0)
    assert math.isclose(pf.positions["BTC"].avg_price, 100.0)


def test_average_cost_blends_two_buys() -> None:
    pf = Portfolio(cash=10_000.0)
    pf.apply(_fill(Side.BUY, 1.0, 100.0))
    pf.apply(_fill(Side.BUY, 1.0, 200.0))
    assert math.isclose(pf.positions["BTC"].avg_price, 150.0)


def test_sell_realizes_pnl() -> None:
    pf = Portfolio(cash=1_000.0)
    pf.apply(_fill(Side.BUY, 2.0, 100.0))
    pf.apply(_fill(Side.SELL, 1.0, 150.0))
    assert math.isclose(pf.realized_pnl(), 50.0)  # 1 unit * (150-100)
    assert math.isclose(pf.positions["BTC"].quantity, 1.0)


def test_unrealized_pnl_and_equity() -> None:
    pf = Portfolio(cash=1_000.0)
    pf.apply(_fill(Side.BUY, 1.0, 100.0))
    marks = {"BTC": 130.0}
    assert math.isclose(pf.unrealized_pnl(marks), 30.0)
    assert math.isclose(pf.equity(marks), 900.0 + 130.0)
    assert math.isclose(pf.total_return(marks), (1030.0 / 1000.0) - 1.0)


def test_fees_accumulate() -> None:
    pf = Portfolio(cash=1_000.0)
    pf.apply(_fill(Side.BUY, 1.0, 100.0, fee=0.5))
    pf.apply(_fill(Side.SELL, 1.0, 110.0, fee=0.55))
    assert math.isclose(pf.total_fees, 1.05)


def test_snapshot_serialises_positions() -> None:
    pf = Portfolio(cash=1_000.0)
    pf.apply(_fill(Side.BUY, 1.0, 100.0))
    snap = PortfolioSnapshot.of(pf, {"BTC": 120.0})
    assert isinstance(snap, PortfolioSnapshot)
    assert math.isclose(snap.equity, 900.0 + 120.0)
    assert snap.positions["BTC"] == 1.0
