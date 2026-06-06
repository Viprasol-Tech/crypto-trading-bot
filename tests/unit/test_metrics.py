"""Tests for the performance-metrics functions."""

from __future__ import annotations

import math

from crypto_trading_bot import metrics


def test_total_return() -> None:
    assert math.isclose(metrics.total_return([100.0, 110.0]), 0.10)
    assert metrics.total_return([100.0]) == 0.0
    assert metrics.total_return([]) == 0.0


def test_returns_step_over_step() -> None:
    rets = metrics.returns([100.0, 110.0, 99.0])
    assert math.isclose(rets[0], 0.10)
    assert math.isclose(rets[1], 99.0 / 110.0 - 1.0)


def test_max_drawdown_simple() -> None:
    # peak 120, trough 90 -> dd = 30/120 = 0.25
    assert math.isclose(metrics.max_drawdown([100, 120, 90, 110]), 0.25)


def test_max_drawdown_monotonic_up_is_zero() -> None:
    assert metrics.max_drawdown([1, 2, 3, 4, 5]) == 0.0


def test_volatility_constant_curve_is_zero() -> None:
    assert metrics.volatility([100.0] * 10) == 0.0


def test_sharpe_zero_when_no_volatility() -> None:
    assert metrics.sharpe_ratio([100.0] * 10) == 0.0


def test_sharpe_positive_for_steady_growth() -> None:
    curve = [100.0 * (1.01**i) for i in range(50)]
    assert metrics.sharpe_ratio(curve) > 0.0


def test_cagr_doubling_in_one_year() -> None:
    curve = [100.0, 200.0]  # 1 step
    val = metrics.cagr(curve, periods_per_year=1)
    assert math.isclose(val, 1.0)  # +100%
