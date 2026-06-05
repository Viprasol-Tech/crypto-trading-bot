<p align="center">
  <img src="docs/assets/logo.png" width="120" alt="Viprasol Tech logo">
</p>

<h1 align="center">Crypto Trading Bot</h1>

<p align="center">
  <strong>Multi-exchange cryptocurrency trading bot with grid, DCA, and momentum strategies — in Python.</strong><br>
  Plug in an exchange, pick a strategy, backtest on the simulated exchange, then go live.
</p>

<p align="center">
  <em>Built and maintained by <a href="https://viprasol.com">Viprasol Tech</a> — Fintech Experts. Full-Stack Builders.</em>
</p>

<p align="center">
  <a href="https://github.com/Viprasol-Tech/crypto-trading-bot/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Viprasol-Tech/crypto-trading-bot/ci.yml?style=flat-square&logo=githubactions&logoColor=white&label=CI" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/Viprasol-Tech/crypto-trading-bot?style=flat-square&color=blue" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <a href="https://t.me/viprasol_help"><img src="https://img.shields.io/badge/Telegram-support-26A5E4?style=flat-square&logo=telegram&logoColor=white" alt="Telegram"></a>
  <a href="https://github.com/Viprasol-Tech/crypto-trading-bot/stargazers"><img src="https://img.shields.io/github/stars/Viprasol-Tech/crypto-trading-bot?style=flat-square&logo=github" alt="Stars"></a>
</p>

---

> ## ⚠️ Disclaimer
> This software is for **educational purposes only** and is **not financial advice**. Cryptocurrency trading is highly volatile and involves substantial risk, including the **total loss of capital**. Backtest results are **not** indicative of future performance. Always test on the simulated exchange first and comply with each exchange's terms and your local laws. **Use at your own risk** — Viprasol Tech assumes no responsibility for your trading results.

---

## ✨ Features

- 🔌 **Multi-exchange ready** — one `Exchange` interface; bring Binance, Coinbase, Kraken, etc.
- 🏜️ **Simulated exchange included** — paper-trade and backtest with no API keys or risk.
- 📊 **Grid strategy** — buy the dips, sell into strength across a configurable price grid.
- 💵 **DCA strategy** — dollar-cost-average a fixed amount on a fixed cadence.
- 🧩 **Pluggable strategies** — pure `price in → orders out`, trivial to test and extend.
- 🖥️ **CLI** — `crypto-trading-bot demo --strategy grid` runs the whole pipeline.
- ⚙️ **Modern tooling** — ruff, mypy (strict), pytest, GitHub Actions CI.

## 🚀 Quickstart

```bash
git clone https://github.com/Viprasol-Tech/crypto-trading-bot.git
cd crypto-trading-bot
python -m pip install -e ".[dev]"

# Run a grid-trading backtest on synthetic data:
crypto-trading-bot demo --strategy grid
crypto-trading-bot demo --strategy dca
```

## 🧩 Write your own strategy

```python
from crypto_trading_bot.strategies.base import Strategy
from crypto_trading_bot.models import Order, Side

class BuyTheDip(Strategy):
    name = "buy_the_dip"
    def on_price(self, symbol, price, exchange):
        if price < 90:
            return [Order(symbol, Side.BUY, 1.0, price)]
        return []
```

## 🏗️ Architecture

```mermaid
flowchart LR
    FEED[Price feed] --> BOT[Trading bot]
    BOT --> STRAT[Strategy: grid / DCA / custom]
    STRAT --> EX[Exchange / SimulatedExchange]
```

## 🗺️ Roadmap

- [x] Simulated exchange + grid + DCA strategies
- [x] Pluggable strategy interface + backtest runner
- [ ] Live exchange adapters (ccxt)
- [ ] Momentum & breakout strategies
- [ ] Telegram alerts and portfolio tracking

## 🤝 Contributing

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📬 Contact — Viprasol Tech Private Limited

- 🌐 Website: [viprasol.com](https://viprasol.com)
- ✉️ Email: [support@viprasol.com](mailto:support@viprasol.com)
- 💬 Telegram: [t.me/viprasol_help](https://t.me/viprasol_help) · 📱 WhatsApp: +91 96336 52112
- 🐙 GitHub: [@Viprasol-Tech](https://github.com/Viprasol-Tech) · 💼 [LinkedIn](https://www.linkedin.com/in/viprasol/) · 𝕏 [@viprasol](https://twitter.com/viprasol)

> *Viprasol Tech — fintech software, algorithmic trading systems, MT4/MT5 bots, AI voice agents, and B2B SaaS. Need a custom build? [Get in touch](mailto:support@viprasol.com).*

## 📄 License

[MIT](LICENSE) © 2025 Viprasol Tech Private Limited
