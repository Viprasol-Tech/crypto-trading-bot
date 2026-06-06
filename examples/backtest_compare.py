"""Example: backtest and compare every built-in strategy programmatically.

Run from the repo root:

    PYTHONPATH=src python examples/backtest_compare.py

This mirrors what ``crypto-trading-bot compare`` does, but shows the public
Python API so you can embed it in your own research notebooks or pipelines.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot import (
    CostModel,
    available_strategies,
    build_strategy,
    run_backtest,
)
from crypto_trading_bot.data import trending


def main() -> None:
    prices = trending(n=300, seed=7)
    costs = CostModel(fee_rate=0.001, slippage_bps=5.0)

    print(f"{'strategy':<16} {'return':>9} {'alpha':>9} {'maxDD':>7} {'sharpe':>7} {'trades':>7}")
    print("-" * 60)

    results = []
    for name in available_strategies():
        report = run_backtest(build_strategy(name), prices, cash=10_000.0, cost_model=costs)
        results.append(report)

    for r in sorted(results, key=lambda x: x.total_return, reverse=True):
        print(
            f"{r.strategy:<16} {r.total_return * 100:>8.2f}% {r.alpha * 100:>8.2f}% "
            f"{r.max_drawdown * 100:>6.2f}% {r.sharpe:>7.2f} {r.n_trades:>7}"
        )

    print("-" * 60)
    print(f"buy & hold baseline: {results[0].buy_and_hold_return * 100:+.2f}%")


if __name__ == "__main__":
    main()
