"""Backtest engine and report.

Replays a price series through a strategy on a fresh simulated exchange,
recording an equity curve and producing a rich :class:`BacktestReport` with
return, drawdown, Sharpe, win rate and fee totals.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from crypto_trading_bot import metrics
from crypto_trading_bot.exchanges.simulated import InsufficientFunds, SimulatedExchange
from crypto_trading_bot.fees import CostModel
from crypto_trading_bot.models import Fill, Side
from crypto_trading_bot.portfolio import Portfolio, PortfolioSnapshot
from crypto_trading_bot.strategies.base import Strategy


@dataclass(slots=True)
class BacktestReport:
    """Summary of a single backtest run."""

    strategy: str
    symbol: str
    bars: int
    starting_equity: float
    final_equity: float
    total_return: float
    buy_and_hold_return: float
    max_drawdown: float
    sharpe: float
    cagr: float
    n_trades: int
    n_buys: int
    n_sells: int
    win_rate: float
    total_fees: float
    portfolio: PortfolioSnapshot
    equity_curve: list[float] = field(default_factory=list)

    @property
    def alpha(self) -> float:
        """Excess total return over buy-and-hold."""
        return self.total_return - self.buy_and_hold_return

    def as_dict(self) -> dict[str, float | int | str]:
        """Flat dict of headline numbers (handy for JSON/CSV export)."""
        return {
            "strategy": self.strategy,
            "symbol": self.symbol,
            "bars": self.bars,
            "final_equity": round(self.final_equity, 2),
            "total_return": round(self.total_return, 4),
            "buy_and_hold_return": round(self.buy_and_hold_return, 4),
            "alpha": round(self.alpha, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "sharpe": round(self.sharpe, 3),
            "cagr": round(self.cagr, 4),
            "n_trades": self.n_trades,
            "win_rate": round(self.win_rate, 4),
            "total_fees": round(self.total_fees, 2),
        }


def _round_trip_win_rate(fills: Sequence[Fill]) -> tuple[float, int]:
    """Pair each SELL against average buy cost so far; return (win_rate, wins).

    Uses running average-cost accounting per asset to label each closing SELL a
    win or loss. Returns ``(0.0, 0)`` if there are no closing trades.
    """
    avg: dict[str, float] = {}
    qty: dict[str, float] = {}
    wins = 0
    closes = 0
    for fill in fills:
        base = fill.order.symbol.split("/")[0]
        q = fill.order.quantity
        price = fill.executed_price
        if fill.order.side is Side.BUY:
            new_q = qty.get(base, 0.0) + q
            avg[base] = (avg.get(base, 0.0) * qty.get(base, 0.0) + price * q) / new_q
            qty[base] = new_q
        else:
            closes += 1
            if price > avg.get(base, price):
                wins += 1
            qty[base] = qty.get(base, 0.0) - q
    return (wins / closes if closes else 0.0, wins)


def run_backtest(
    strategy: Strategy,
    prices: Sequence[float],
    *,
    symbol: str = "BTC/USDT",
    cash: float = 10_000.0,
    cost_model: CostModel | None = None,
) -> BacktestReport:
    """Replay ``prices`` through ``strategy`` and return a full report."""
    if not prices:
        raise ValueError("prices must not be empty")
    quote = symbol.split("/")[1]
    exchange = SimulatedExchange(balances={quote: cash}, cost_model=cost_model)
    portfolio = Portfolio(cash=cash, quote=quote)
    fills: list[Fill] = []
    equity_curve: list[float] = []

    for price in prices:
        exchange.set_price(symbol, price)
        for order in strategy.on_price(symbol, price, exchange):
            try:
                fill = exchange.execute(order)
            except InsufficientFunds:
                continue
            fills.append(fill)
            portfolio.apply(fill)
        equity_curve.append(exchange.equity(quote))

    marks = {symbol.split("/")[0]: prices[-1]}
    win_rate, _ = _round_trip_win_rate(fills)
    bnh = prices[-1] / prices[0] - 1.0 if prices[0] else 0.0
    n_buys = sum(1 for f in fills if f.order.side is Side.BUY)
    return BacktestReport(
        strategy=strategy.name,
        symbol=symbol,
        bars=len(prices),
        starting_equity=cash,
        final_equity=equity_curve[-1],
        total_return=metrics.total_return(equity_curve),
        buy_and_hold_return=bnh,
        max_drawdown=metrics.max_drawdown(equity_curve),
        sharpe=metrics.sharpe_ratio(equity_curve),
        cagr=metrics.cagr(equity_curve),
        n_trades=len(fills),
        n_buys=n_buys,
        n_sells=len(fills) - n_buys,
        win_rate=win_rate,
        total_fees=portfolio.total_fees,
        portfolio=PortfolioSnapshot.of(portfolio, marks),
        equity_curve=equity_curve,
    )
