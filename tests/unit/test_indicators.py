"""Tests for the streaming technical indicators."""

from __future__ import annotations

import math

import pytest

from crypto_trading_bot.indicators import EMA, RSI, SMA, RollingExtrema


def test_sma_is_none_until_full_then_averages() -> None:
    sma = SMA(3)
    assert sma.update(1.0) is None
    assert sma.update(2.0) is None
    assert math.isclose(sma.update(3.0) or 0.0, 2.0)
    assert math.isclose(sma.update(6.0) or 0.0, (2 + 3 + 6) / 3)


def test_sma_rejects_bad_period() -> None:
    with pytest.raises(ValueError):
        SMA(0)


def test_ema_seeds_with_sma_then_smooths() -> None:
    ema = EMA(3)
    assert ema.update(2.0) is None
    assert ema.update(4.0) is None
    seeded = ema.update(6.0)
    assert seeded is not None and math.isclose(seeded, 4.0)  # SMA of first 3
    nxt = ema.update(8.0)
    assert nxt is not None and nxt > seeded  # moves toward the new price


def test_ema_tracks_a_constant_series() -> None:
    ema = EMA(5)
    last = None
    for _ in range(20):
        last = ema.update(100.0)
    assert last is not None and math.isclose(last, 100.0)


def test_rsi_is_100_on_monotonic_rise() -> None:
    rsi = RSI(5)
    value = None
    for price in range(1, 30):
        value = rsi.update(float(price))
    assert value is not None and math.isclose(value, 100.0)


def test_rsi_is_low_on_monotonic_fall() -> None:
    rsi = RSI(5)
    value = None
    for price in range(30, 1, -1):
        value = rsi.update(float(price))
    assert value is not None and value < 5.0


def test_rsi_stays_bounded() -> None:
    rsi = RSI(14)
    seq = [10, 12, 11, 13, 9, 15, 14, 16, 12, 18, 17, 19, 11, 20, 21, 10]
    for price in seq:
        v = rsi.update(float(price))
        if v is not None:
            assert 0.0 <= v <= 100.0


def test_rolling_extrema_tracks_window() -> None:
    ext = RollingExtrema(3)
    for price in (5.0, 1.0, 9.0):
        ext.update(price)
    assert ext.ready
    assert ext.high == 9.0
    assert ext.low == 1.0
    ext.update(2.0)  # drops the 5.0
    assert ext.high == 9.0
    assert ext.low == 1.0
    ext.update(3.0)  # drops the 1.0 -> window {9,2,3}
    assert ext.low == 2.0
