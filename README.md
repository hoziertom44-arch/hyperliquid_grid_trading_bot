# Grid Trading Hyperliquid Bot

> **Built by Tom Hozier · RektCoder**
> 🎁 Sign up to Hyperliquid via my link for a **4% lifetime fee discount** → [hyperliquid.xyz/join/REKTCODER](https://app.hyperliquid.xyz/join/REKTCODER)
> 📢 Updates & support → [t.me/rektcoderchannel](https://t.me/rektcoderchannel)

A grid trading bot for Hyperliquid perpetuals. Python, built on the official Hyperliquid SDK, with a hedge-fund themed live terminal dashboard powered by [Rich](https://github.com/Textualize/rich).

- 📈 Posts maker-only limit orders to earn **rebates instead of paying fees**
- 🛡️ Drawdown circuit breaker + range-break protection
- 🪞 Live grid ladder, market panel, position, and P&L all in one screen
- 🔐 Uses API wallet keys — bot can trade but **cannot withdraw your funds**
- 📡 Optional Telegram alerts on fills, range breaks, drawdowns

---

## ⚠️ Step 0 — Sign up to Hyperliquid first

If you don't have a Hyperliquid account yet:

🔗 **https://app.hyperliquid.xyz/join/REKTCODER**

This gives you a 4% lifetime fee discount AND supports the channel (free bots cost real time to build). The referral can only be set BEFORE your first trade, so use the link or paste the code `REKTCODER` on `app.hyperliquid.xyz/referrals` before doing anything else.

Already have a Hyperliquid account? You can't change your referrer (Hyperliquid binds it permanently on first trade), but you can still run this bot.

---

## Quick Start

### 1. Install Python 3.10+ and dependencies

```bash
python -m venv .venv
source .venv/bin/activate         # macOS/Linux
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 2. Set up credentials

```bash
cp .env .env
```

Open `.env` and fill in:

- **HYPERLIQUID_API_WALLET_PRIVATE_KEY** — generate at [app.hyperliquid.xyz/API](https://app.hyperliquid.xyz/API). API wallets can trade but CANNOT withdraw your funds.
- **HYPERLIQUID_ACCOUNT_ADDRESS** — your main wallet address (the one that holds USDC on Hyperliquid).

Both are required.

### 3. Tune the grid

Open `config.yaml`:

```yaml
asset: "BTC"               # BTC, ETH, SOL, HYPE, etc.
network: "mainnet"         # mainnet or testnet
range_mode: "auto"         # auto = current_price ± range_pct
range_pct: 3.0             # ±3%
grid_levels: 20            # 4–100
capital_usdc: 200.0        # total capital
leverage: 5                # 1–40
max_drawdown_pct: 15.0     # pause if equity drops this %
```

### 4. Run

```bash
python run.py
```

You'll see the banner, then the live dashboard with grid ladder, market data, position, and P&L all updating in real-time.

**Stop cleanly with Ctrl+C** — the bot cancels all its grid orders before exiting.

---

## What You'll See

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                              ┃
┃   G R I D   T R A D I N G   H Y P E R L I Q U I D            ┃
┃                       B O T                                  ┃
┃                                                              ┃
┃   Built by Tom Hozier · RektCoder · @rektcoder_              ┃
┃                                                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ SESSION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Network    MAINNET · LIVE TRADING                          ┃
┃  Asset      BTC                                             ┃
┃  Capital    $200.00 USDC                                    ┃
┃  Leverage   5x                                              ┃
┃  Account    0x1234…cdef                                     ┃
┃                                                             ┃
┃  ╭─────────────────────────────────────────────────────╮    ┃
┃  │  REKTCODER REF  https://app.hyperliquid.xyz/join/…  │    ┃
┃  │  Telegram       https://t.me/rektcoderchannel       │    ┃
┃  ╰─────────────────────────────────────────────────────╯    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─ MARKET ─────────────────┐  ┌─ POSITION ──────────────────┐
│ Mid Price  $100,234.50    │  │ Net Position  +0.001992 BTC │
│ 24h Change +1.42%         │  │ Avg Entry     $97,378.50    │
│ Best Bid   $100,234.00    │  │ Unrealized    +$5.71        │
│ Best Ask   $100,235.00    │  │ Return        +0.59%        │
└──────────────────────────┘  └─────────────────────────────┘

┌─ GRID LADDER ─────────────────────────────────────────────┐
│ Levels  20    Spacing  $300.00                            │
│ Lower   $97,228.40    Upper   $103,240.50                 │
│                                                           │
│ Status   Side   Price          Size       Fills   OID     │
│ OPEN     SELL   $103,240.50    0.000996   0       fa3e21  │
│ OPEN     SELL   $102,940.40    0.000996   0       ab12cd  │
│ …                                                         │
│ OPEN     BUY    $100,234.50 ←  0.000996   0       8d9ee2  │
│ …                                                         │
│ OPEN     BUY    $97,228.40     0.000996   0       441f0c  │
└───────────────────────────────────────────────────────────┘

┌─ SESSION P&L ──────────────────────────────────────────────┐
│ Fills         12          Volume         $24,000.00        │
│ Realized P&L  +$18.20     Maker Rebates  +$3.60            │
│ Drawdown      -0.45%      Uptime         3m 47s            │
│ Equity        $223.91     Peak           $225.00           │
└────────────────────────────────────────────────────────────┘
```

The whole thing updates twice a second.

---

## How Grid Trading Works (3 Sentences)

The bot places **BUY orders below** the current price and **SELL orders above**, evenly spaced. When a BUY fills, it places a new SELL one level above (and vice versa). Each round trip captures the **grid spacing minus fees** as profit, so a choppy sideways market generates dozens of trades per day.

**Best in:** sideways/choppy markets. **Worst in:** strong directional trends.

---

## Configuration Reference

See `config.yaml`. Key knobs:

| Setting | Purpose |
|---|---|
| `asset` | Trading pair (BTC, ETH, SOL, HYPE, etc.) |
| `network` | `mainnet` (real money) or `testnet` (paper) |
| `range_mode` | `auto` (current price ± pct) or `manual` |
| `range_pct` | Auto range width as % of mid |
| `grid_levels` | Number of grid divisions (4–100) |
| `capital_usdc` | Total capital |
| `leverage` | Multiplier (1–40) |
| `post_only` | True = ALO post-only for maker rebates |
| `max_drawdown_pct` | Equity drawdown that triggers pause |
| `range_break_pct` | Distance outside range that triggers pause |
| `verbose_logging` | Render full dashboard each tick |
| `telegram_enabled` | Send Telegram alerts (also requires .env tokens) |

---

## Honest Limitations

- **Grids lose in strong trends.** If price drops 10% straight down, the bot keeps buying all the way → you bag-hold. The drawdown circuit breaker limits damage but won't eliminate it.
- **Maker rebates depend on order routing.** With `post_only: true`, orders that would cross the spread get rejected. You miss some fills but never pay taker fees.
- **Fill detection is reconciliation-based.** The bot polls open orders every `refresh_interval_seconds` to detect fills. Default is 5s — there's a small lag.
- **Single-asset only.** Run multiple instances for multi-asset.

See `ONBOARDING.md` for the beginner-friendly walkthrough including wallet setup, USDC deposit, and API wallet creation.

---

## Built by Tom Hozier · RektCoder

- 🎁 **Hyperliquid:** https://app.hyperliquid.xyz/join/REKTCODER
- 📢 **Telegram:** https://t.me/rektcoderchannel
- ▶ **YouTube:** [@rektcoder](https://youtube.com/@rektcoder)
- 𝕏 **Twitter:** [@rektcoder_](https://twitter.com/rektcoder_)

If this bot helps you, **the biggest support is signing up to Hyperliquid via my link** — it costs you nothing (you save 4% in fees) and helps fund more open-source bot content.

---

**Disclaimer:** Trading perpetuals with leverage carries substantial risk including total loss of capital. Past performance does not predict future results. This bot is provided as-is. Test on testnet before going live with real money.
