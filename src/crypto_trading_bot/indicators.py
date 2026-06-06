"""Lightweight, dependency-free technical indicators.

Each indicator is a tiny stateful object: feed it one price at a time with
``update(price)`` and read ``.value`` (``None`` until enough data has arrived).
This streaming design mirrors how a live bot consumes a price feed and keeps
strategies pure and trivially testable.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from collections import deque


class SMA:
    """Simple Moving Average over a fixed window."""

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError("period must be >= 1")
        self.period = period
        self._window: deque[float] = deque(maxlen=period)
        self.value: float | None = None

    @property
    def ready(self) -> bool:
        return len(self._window) == self.period

    def update(self, price: float) -> float | None:
        self._window.append(price)
        self.value = sum(self._window) / len(self._window) if self.ready else None
        return self.value


class EMA:
    """Exponential Moving Average (Wilder-style smoothing seeded by the first SMA)."""

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError("period must be >= 1")
        self.period = period
        self._alpha = 2.0 / (period + 1.0)
        self._seed: list[float] = []
        self.value: float | None = None

    @property
    def ready(self) -> bool:
        return self.value is not None

    def update(self, price: float) -> float | None:
        if self.value is None:
            self._seed.append(price)
            if len(self._seed) == self.period:
                self.value = sum(self._seed) / self.period
            return self.value
        self.value += self._alpha * (price - self.value)
        return self.value


class RSI:
    """Relative Strength Index (Wilder smoothing), bounded 0-100."""

    def __init__(self, period: int = 14) -> None:
        if period < 1:
            raise ValueError("period must be >= 1")
        self.period = period
        self._prev: float | None = None
        self._avg_gain = 0.0
        self._avg_loss = 0.0
        self._count = 0
        self.value: float | None = None

    @property
    def ready(self) -> bool:
        return self.value is not None

    def update(self, price: float) -> float | None:
        if self._prev is None:
            self._prev = price
            return None
        change = price - self._prev
        self._prev = price
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        self._count += 1
        if self._count <= self.period:
            self._avg_gain += gain / self.period
            self._avg_loss += loss / self.period
            if self._count < self.period:
                return None
        else:
            self._avg_gain = (self._avg_gain * (self.period - 1) + gain) / self.period
            self._avg_loss = (self._avg_loss * (self.period - 1) + loss) / self.period
        if self._avg_loss == 0.0:
            self.value = 100.0
        else:
            rs = self._avg_gain / self._avg_loss
            self.value = 100.0 - (100.0 / (1.0 + rs))
        return self.value


class RollingExtrema:
    """Tracks the rolling high and low over a fixed lookback window."""

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError("period must be >= 1")
        self.period = period
        self._window: deque[float] = deque(maxlen=period)

    @property
    def ready(self) -> bool:
        return len(self._window) == self.period

    @property
    def high(self) -> float | None:
        return max(self._window) if self._window else None

    @property
    def low(self) -> float | None:
        return min(self._window) if self._window else None

    def update(self, price: float) -> None:
        self._window.append(price)
