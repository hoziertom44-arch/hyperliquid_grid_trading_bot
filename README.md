<div align="center">

# 🤖 Grid Trading Hyperliquid Bot

### *The grid bot that trades while you sleep.*

[![Built by RektCoder](https://img.shields.io/badge/built%20by-RektCoder-6FE8B6?style=for-the-badge)](https://youtube.com/@rektcoder)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Hyperliquid](https://img.shields.io/badge/exchange-Hyperliquid-50D2C2?style=for-the-badge)](https://app.hyperliquid.xyz/join/REKTCODER)
[![Free & Open Source](https://img.shields.io/badge/100%25-free%20%26%20open%20source-00C853?style=for-the-badge)](#)

<br/>

[![Watch the full tutorial](https://img.youtube.com/vi/N4W06Rybn_0/maxresdefault.jpg)](https://youtu.be/N4W06Rybn_0)

### ▶️ [**Watch the full setup tutorial on YouTube**](https://youtu.be/N4W06Rybn_0)

<br/>

[🎁 Sign up to Hyperliquid](https://app.hyperliquid.xyz/join/REKTCODER) · [📢 Join the Telegram](https://t.me/rektcoderchannel) · [▶️ Subscribe on YouTube](https://youtube.com/@rektcoder) · [𝕏 Twitter](https://twitter.com/rektcoder_)

</div>

---

## 📑 Table of Contents

- [⚡ What This Bot Does](#-what-this-bot-does)
- [✨ Features](#-features)
- [🎯 Step 0 — Sign Up to Hyperliquid](#-step-0--sign-up-to-hyperliquid)
- [🚀 Quick Start](#-quick-start)
- [📺 What You'll See](#-what-youll-see)
- [📚 How Grid Trading Works](#-how-grid-trading-works)
- [⚙️ Configuration Reference](#️-configuration-reference)
- [🛡️ Risk Controls](#️-risk-controls)
- [⚠️ Honest Limitations](#️-honest-limitations)
- [🆘 Troubleshooting](#-troubleshooting)
- [💚 Support the Channel](#-support-the-channel)
- [📜 License & Disclaimer](#-license--disclaimer)

---

## ⚡ What This Bot Does

This is an **automated grid trading bot** for [Hyperliquid](https://app.hyperliquid.xyz/join/REKTCODER) perpetuals. It places a ladder of buy orders below the current price and sell orders above it, then refills the grid every time price moves through a level. The result is a continuous capture of market volatility, no directional bet required.

> 💡 **In plain English:** You give the bot some USDC. It trades all day. You sleep. It harvests small profits every time price wobbles. That's it.

---

## ✨ Features

| Feature | What It Does |
|---|---|
| 📈 **Maker-only orders** | Uses post-only (`Alo`) orders to **earn rebates** instead of paying taker fees |
| 🛡️ **Drawdown circuit breaker** | Auto-pauses the bot if your equity drops below your risk threshold |
| 🪞 **Live terminal dashboard** | Hedge-fund themed UI powered by [Rich](https://github.com/Textualize/rich) — market data, grid ladder, position, P&L all on one screen |
| 🔐 **API wallet only** | Bot can trade but **cannot withdraw your funds**. Even a leaked key keeps your money safe |
| 📡 **Telegram alerts** | Optional notifications on every fill, range break, and drawdown event |
| 🔄 **Auto re-anchoring** | If price exits the range, the bot pauses and waits for re-entry |
| 🐍 **Pure Python** | Built on the [official Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk). No black box magic |
| 💯 **Free forever** | Open source. No paywall. No premium tier. No upsell |

---

## 🎁 Step 0 — Sign Up to Hyperliquid

> If you haven't already, **this is the most important step**.

<div align="center">

### 🔗 [**app.hyperliquid.xyz/join/REKTCODER**](https://app.hyperliquid.xyz/join/REKTCODER)

</div>

You get a **4% lifetime fee discount** on every trade you ever make on Hyperliquid. The referral can only be set **before your first trade**, so use the link or paste the code `REKTCODER` at [app.hyperliquid.xyz/referrals](https://app.hyperliquid.xyz/referrals) before doing anything else.

Already trading on Hyperliquid? You can still run the bot, but your fee discount is locked to whatever code you used at signup.

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

You'll need:
- **Python 3.10 or higher** — [python.org/downloads](https://www.python.org/downloads/)
  - On Windows, tick **"Add Python to PATH"** during install
- **PyCharm** *(optional but recommended)* — [jetbrains.com/pycharm](https://www.jetbrains.com/pycharm/) (the free Community Edition works perfectly)
- **A Hyperliquid account** with at least **$40 USDC** funded for perps trading

### 2️⃣ Clone the repo

```bash
git clone https://github.com/hoziertom44-arch/hyperliquid_frid_trading_bot.git
cd hyperliquid_frid_trading_bot
```

### 3️⃣ Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate         # macOS / Linux
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 4️⃣ Set up credentials

```bash
cp .env.example .env
```

Open `.env` and fill in:

| Variable | What it is | How to get it |
|---|---|---|
| `HYPERLIQUID_API_WALLET_PRIVATE_KEY` | The bot's signing key | Generate at [app.hyperliquid.xyz/API](https://app.hyperliquid.xyz/API) |
| `HYPERLIQUID_ACCOUNT_ADDRESS` | Your main wallet address | Click your email in the top-right corner on Hyperliquid |

> ⚠️ **Use an API wallet, not your main wallet seed.** API wallets can trade but **cannot withdraw funds**. Even if leaked, your money stays safe.

### 5️⃣ Tune the grid

Open `config.yaml`:

```yaml
asset: "BTC"               # Trading pair (BTC, ETH, SOL, HYPE...)
network: "mainnet"         # mainnet = real money. testnet = paper
range_mode: "auto"         # auto picks the range for you
range_pct: 3.0             # ±3% from current price
grid_levels: 20            # number of grid divisions
capital_usdc: 200.0        # total capital
leverage: 5                # 1–40x
max_drawdown_pct: 15.0     # pause if equity drops this %
```

### 6️⃣ Run

```bash
python run.py
```

The hedge-fund dashboard fires up, the bot places its grid, and you're trading.

**Stop cleanly with `Ctrl + C`** — the bot will cancel all its open orders before exiting.

---

## 📺 What You'll See

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   G R I D   T R A D I N G   H Y P E R L I Q U I D              ┃
┃                       B O T                                     ┃
┃   Built by Tom Hozier · RektCoder · @rektcoder_                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━ SESSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Network    MAINNET · LIVE TRADING                              ┃
┃ Asset      BTC                                                 ┃
┃ Capital    $200.00 USDC                                        ┃
┃ Leverage   5x                                                  ┃
┃ Account    0x1234…cdef                                         ┃
┃                                                                ┃
┃ REKTCODER REF  https://app.hyperliquid.xyz/join/REKTCODER     ┃
┃ Telegram       https://t.me/rektcoderchannel                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─ MARKET ──────────────────┐  ┌─ POSITION ────────────────┐
│ Mid Price   $100,234.50    │  │ Net Position +0.001992 BTC │
│ 24h Change  +1.42%         │  │ Avg Entry    $97,378.50    │
│ Best Bid    $100,234.00    │  │ Unrealized   +$5.71        │
│ Best Ask    $100,235.00    │  │ Return       +0.59%        │
└───────────────────────────┘  └──────────────────────────┘

┌─ GRID LADDER ────────────────────────────────────────────────┐
│ Levels  20    Spacing  $300.00                               │
│ Lower   $97,228.40    Upper   $103,240.50                    │
│                                                              │
│ Status  Side   Price          Size       Fills   OID         │
│ OPEN    SELL   $103,240.50    0.000996   0       fa3e21      │
│ OPEN    SELL   $102,940.40    0.000996   0       ab12cd      │
│ ...                                                          │
│ OPEN    BUY    $100,234.50 ←  0.000996   0       8d9ee2      │
│ ...                                                          │
│ OPEN    BUY    $97,228.40     0.000996   0       441f0c      │
└─────────────────────────────────────────────────────────────┘

┌─ SESSION P&L ────────────────────────────────────────────────┐
│ Fills         12          Volume         $24,000.00          │
│ Realized P&L  +$18.20     Maker Rebates  +$3.60              │
│ Drawdown      -0.45%      Uptime         3m 47s              │
│ Equity        $223.91     Peak           $225.00             │
└─────────────────────────────────────────────────────────────┘
```

Updates **twice per second** with live market data.

---

## 📚 How Grid Trading Works

A grid bot places **buy orders below** the current price and **sell orders above** it, evenly spaced across a defined range.

```
                          $103,000 → SELL ← profit zone
                          $102,000 → SELL ←
       sell zone          $101,000 → SELL ←
─────────────────────────────────────────────
                          $100,000 → MID  ← (current price)
─────────────────────────────────────────────
       buy zone           $99,000  → BUY  ← profit zone
                          $98,000  → BUY  ←
                          $97,000  → BUY  ←
```

When price moves UP and triggers a SELL → the bot places a new BUY one level below.
When price moves DOWN and triggers a BUY → the bot places a new SELL one level above.

Every round trip captures the **grid spacing minus fees** as profit. The bot doesn't predict direction. It just **harvests volatility**.

### 🌊 When grids win

✅ Sideways, choppy markets
✅ Range-bound consolidation
✅ Crab markets where price oscillates within a defined channel

### 🌪️ When grids struggle

❌ Strong directional trends (the bot bag-holds inventory)
❌ Black swan dumps that exit the range and never return
❌ Markets with extreme volatility that breaks the range repeatedly

---

## ⚙️ Configuration Reference

All knobs live in [`config.yaml`](config.yaml):

| Setting | Default | Purpose |
|---|---|---|
| `asset` | `BTC` | Trading pair (BTC, ETH, SOL, HYPE, etc.) |
| `network` | `mainnet` | `mainnet` (real money) or `testnet` (paper) |
| `range_mode` | `auto` | `auto` (current price ± pct) or `manual` |
| `range_pct` | `3.0` | Auto range width as % of mid |
| `grid_levels` | `20` | Number of grid divisions (4–100) |
| `capital_usdc` | `200.0` | Total capital deployed |
| `leverage` | `5` | Multiplier (1–40) |
| `post_only` | `true` | True = ALO post-only for maker rebates |
| `max_drawdown_pct` | `15.0` | Equity drawdown that triggers pause |
| `range_break_pct` | `1.5` | Distance outside range that triggers pause |
| `refresh_interval_seconds` | `5` | How often to reconcile fills |
| `verbose_logging` | `true` | Render full dashboard each tick |
| `telegram_enabled` | `false` | Enable Telegram alerts |

---

## 🛡️ Risk Controls

| Control | What It Does |
|---|---|
| 🚨 **Max Drawdown** | Auto-pauses new orders when equity drops below `max_drawdown_pct` from peak |
| 🚪 **Range Break** | Pauses replacements when price exits the range by `range_break_pct` |
| 🔐 **API Wallet Isolation** | Bot key can trade but **cannot withdraw funds** |
| 🛑 **Clean Shutdown** | Ctrl+C cancels all open orders before exiting |
| 📡 **Telegram Alerts** | Get notified instantly on every drawdown / range break event |

---

## ⚠️ Honest Limitations

> This isn't a money printer. Here's what you should know before deploying real capital.

- **Grids lose in strong trends.** If price drops 10% straight down, the bot keeps buying all the way → you bag-hold. The drawdown circuit breaker limits damage but won't eliminate it.
- **Maker rebates depend on order routing.** With `post_only: true`, orders that would cross the spread get rejected. You miss some fills but never pay taker fees.
- **Fill detection is reconciliation-based.** The bot polls open orders every `refresh_interval_seconds` to detect fills. Default is 5s — there's a small lag.
- **Single-asset only.** Each bot instance trades one asset. Run multiple instances for multi-asset.
- **Minimum $10 USDC notional per order.** Hyperliquid rejects smaller orders. Plan your `capital × leverage / grid_levels` math accordingly.

---

## 🆘 Troubleshooting

<details>
<summary><b>❌ "User or API Wallet does not exist"</b></summary>

You generated your API wallet on mainnet but your config says `network: testnet` (or vice versa). API wallets are network-specific. Either switch the network in `config.yaml` to match where you authorized the key, or generate a new API wallet on the network you want to use.
</details>

<details>
<summary><b>❌ "Order rejected" near the mid price</b></summary>

Expected. Post-only orders that would cross the spread get cancelled by design. Your money stays safe from accidental taker fees. The orders away from mid will still rest cleanly.
</details>

<details>
<summary><b>❌ "Order has invalid size" for every order</b></summary>

Your order notional is below Hyperliquid's $10 minimum. Math check:

```
order_notional = capital × leverage / grid_levels
```

If that's under $10, either increase capital, increase leverage, or reduce grid_levels. Example: $40 capital × 5x leverage / 20 levels = $10 per order ✓
</details>

<details>
<summary><b>❌ Bot crashes on startup with credential error</b></summary>

Open `.env` and verify both values:
- `HYPERLIQUID_API_WALLET_PRIVATE_KEY` should be a **64-char hex string** starting with `0x`
- `HYPERLIQUID_ACCOUNT_ADDRESS` should be a **42-char address** starting with `0x`

If you pasted the same value into both fields, that's the bug — they're different.
</details>

<details>
<summary><b>❌ "drawdown breach" — bot paused</b></summary>

Safety net firing as designed. Your account dropped by `max_drawdown_pct`. Either wait for price to recover (bot resumes automatically), stop the bot and review your range/leverage, or top up your USDC balance.
</details>

---

## 💚 Support the Channel

If this bot helped you, **the single biggest thank you** is signing up to Hyperliquid via my link. It saves YOU 4% in fees forever AND helps fund more open-source bot content.

<div align="center">

### 🎁 [**app.hyperliquid.xyz/join/REKTCODER**](https://app.hyperliquid.xyz/join/REKTCODER)

</div>

**Other ways to support:**

- ⭐ **Star this repo** — it boosts visibility for new viewers
- ▶️ **Subscribe** on [YouTube](https://youtube.com/@rektcoder) — every video is free and open source
- 📢 **Join** the [Telegram community](https://t.me/rektcoderchannel) for updates, support, and the next bot drop
- 𝕏 **Follow** [@rektcoder_](https://twitter.com/rektcoder_) for build-in-public threads
- 🪙 **Use my Hyperliquid link** when signing up new accounts — it costs you nothing

---

## 📜 License & Disclaimer

**License:** MIT — fork it, modify it, ship it, do whatever.

**Disclaimer:** Trading perpetuals with leverage carries substantial risk including total loss of capital. Past performance does not predict future results. This bot is provided as-is, with no warranty of any kind. You are responsible for all trades placed by it. Test on testnet first. Start small. Never deploy capital you cannot afford to lose.

---

<div align="center">

### Built with 💚 by [Tom Hozier](https://youtube.com/@rektcoder) · **RektCoder**

[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@rektcoder)
[![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/rektcoderchannel)
[![Twitter](https://img.shields.io/badge/Twitter-000000?style=for-the-badge&logo=x&logoColor=white)](https://twitter.com/rektcoder_)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/hoziertom44-arch)

**⭐ If this helped you, drop a star ⭐**

</div>
