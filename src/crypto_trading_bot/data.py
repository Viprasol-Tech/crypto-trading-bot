"""Deterministic synthetic price generators for demos and tests.

These are *not* market data — they are reproducible toy series (seeded) so demos
and the test-suite behave identically everywhere. Real adapters live behind the
``Exchange`` interface.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable


def sine_wave(
    n: int = 200, base: float = 100.0, amplitude: float = 15.0, period: float = 20.0
) -> list[float]:
    """A clean oscillating series - ideal for grid / mean-reversion strategies."""
    return [base + amplitude * math.sin(2 * math.pi * i / period) for i in range(n)]


def trending(
    n: int = 200, base: float = 100.0, drift: float = 0.4, noise: float = 1.5, seed: int = 7
) -> list[float]:
    """An up-trending random walk - ideal for momentum / breakout strategies."""
    rng = random.Random(seed)
    price = base
    out: list[float] = []
    for _ in range(n):
        price = max(1.0, price + drift + rng.uniform(-noise, noise))
        out.append(price)
    return out


def random_walk(
    n: int = 200, base: float = 100.0, noise: float = 2.0, seed: int = 42
) -> list[float]:
    """A driftless random walk - a tough, realistic baseline."""
    rng = random.Random(seed)
    price = base
    out: list[float] = []
    for _ in range(n):
        price = max(1.0, price + rng.uniform(-noise, noise))
        out.append(price)
    return out


SERIES: dict[str, Callable[..., list[float]]] = {
    "sine": sine_wave,
    "trend": trending,
    "random": random_walk,
}


def make_series(kind: str = "sine", n: int = 200) -> list[float]:
    """Build one of the named synthetic series."""
    if kind not in SERIES:
        raise ValueError(f"unknown series {kind!r}; choose from {sorted(SERIES)}")
    return SERIES[kind](n=n)
