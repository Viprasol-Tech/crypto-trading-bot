"""Core types for the crypto trading bot.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    """Order side."""

    BUY = "buy"
    SELL = "sell"


@dataclass(slots=True, frozen=True)
class Order:
    """A limit or market order."""

    symbol: str
    side: Side
    quantity: float
    price: float


@dataclass(slots=True)
class Fill:
    """A filled order."""

    order: Order
    fee: float = 0.0
