# Changelog

All notable changes to this project are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[SemVer](https://semver.org/).

## [0.2.0] - 2026-06-06

### Added
- **Three new strategies**: `MomentumStrategy` (dual-EMA crossover),
  `MeanReversionStrategy` (RSI oversold/overbought), and `BreakoutStrategy`
  (Donchian-channel breakout), joining the existing grid and DCA strategies.
- **Streaming technical indicators** module (`indicators.py`): `SMA`, `EMA`,
  `RSI`, and `RollingExtrema` — stateful, dependency-free, one price at a time.
- **Cost model** (`fees.py`): proportional taker fees plus basis-point slippage,
  applied to every fill so backtests and paper trades stay honest.
- **Portfolio tracker** (`portfolio.py`): average-cost positions, realized and
  unrealized PnL, fee totals, equity, and serialisable snapshots.
- **Performance metrics** (`metrics.py`): total return, max drawdown, volatility,
  annualised Sharpe ratio, and CAGR.
- **Backtest engine + report** (`backtest.py`): `run_backtest()` produces a rich
  `BacktestReport` with return vs buy-and-hold (alpha), drawdown, Sharpe, win
  rate, fees, and the full equity curve.
- **Pydantic config + strategy registry** (`config.py`): `BotConfig` validates a
  full run; `build_strategy()` / `available_strategies()` drive the CLI.
- **Synthetic data generators** (`data.py`): deterministic `sine`, `trend`, and
  `random` price series for reproducible demos and tests.
- **CLI subcommands**: `strategies`, `backtest` (with `--json`), and `compare`
  (ranks every strategy) join `version` and an enriched `demo`.
- **Example script** `examples/backtest_compare.py` showing the public Python API.
- Roughly **14x more tests** (4 -> 57) covering indicators, every strategy, the
  cost model, portfolio, metrics, backtest engine, config, and CLI.

### Changed
- `SimulatedExchange` now uses the `CostModel` (fees + slippage), exposes
  `balances`, and rejects unaffordable orders with `InsufficientFunds` (opt out
  with `allow_short=True`). The `fee_rate` argument remains supported.
- `Fill` now records the actual `fill_price` (after slippage) and exposes
  `executed_price` and `notional`.
- `TradingBot` now tracks an equity curve and an embedded `Portfolio`.
- Top-level package re-exports the most-used classes for ergonomic imports.

## [0.1.0] - 2025

### Added
- Initial release of crypto-trading-bot: multi-exchange crypto trading bot with
  grid and DCA strategies, a simulated exchange, and a CLI demo.
