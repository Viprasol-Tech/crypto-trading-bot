"""Mean-reversion (RSI) strategy.

Buys when RSI falls into oversold territory (price stretched below its mean) and
sells when RSI climbs into overbought territory — betting that price snaps back
toward fair value. Works best in ranging, mean-reverting markets.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.indicators import RSI
from crypto_trading_bot.models import Order, Side
from crypto_trading_bot.strategies.base import Strategy


class MeanReversionStrategy(Strategy):
    """RSI oversold/overbought reversion.

    Args:
        period: RSI lookback period.
        oversold: Buy when RSI drops below this threshold.
        overbought: Sell when RSI rises above this threshold.
        quantity: Base-asset quantity traded per signal.
    """

    name = "mean_reversion"

    def __init__(
        self,
        period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        quantity: float = 1.0,
    ) -> None:
        if not 0.0 < oversold < overbought < 100.0:
            raise ValueError("require 0 < oversold < overbought < 100")
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        self.oversold = oversold
        self.overbought = overbought
        self.quantity = quantity
        self._rsi = RSI(period)
        self._holding = False

    def on_price(self, symbol: str, price: float, exchange: Exchange) -> list[Order]:
        rsi = self._rsi.update(price)
        if rsi is None:
            return []
        base = symbol.split("/")[0]
        if rsi <= self.oversold and not self._holding:
            self._holding = True
            return [Order(symbol, Side.BUY, self.quantity, price)]
        if rsi >= self.overbought and self._holding and exchange.balance(base) >= self.quantity:
            self._holding = False
            return [Order(symbol, Side.SELL, self.quantity, price)]
        return []
