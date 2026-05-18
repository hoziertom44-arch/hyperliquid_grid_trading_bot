# 🚀 Onboarding Guide — From Zero to Running Bot

> **Built by Tom Hozier · RektCoder**
> If you've never used Hyperliquid before, follow this guide top-to-bottom.

This guide assumes nothing. By the end you'll have:

1. ✅ A crypto wallet
2. ✅ USDC deposited on Hyperliquid
3. ✅ A 4% lifetime fee discount via my referral
4. ✅ An API wallet for safe bot trading
5. ✅ The grid bot running

**Estimated time:** 30–45 minutes for first-timers. 10 minutes if you already have a wallet + USDC.

---

## Step 1 — Install a Crypto Wallet

You need a Web3 wallet to connect to Hyperliquid. Two great options:

- **[Rabby](https://rabby.io)** (recommended — designed for trading, cleaner UX)
- **[MetaMask](https://metamask.io)** (most popular)

After install:
1. Create a new wallet
2. **Write down your seed phrase** on paper. Store it somewhere safe and offline. **Never** type it into a website, send it to anyone, or store it digitally. If anyone has your seed phrase, they own your crypto.
3. Your **public address** (the `0x…` string) is what people use to send you crypto. It's safe to share.

---

## Step 2 — Get USDC

You need USDC (a US dollar stablecoin) to trade on Hyperliquid.

### From an Indian exchange (CoinDCX, CoinSwitch, WazirX):

1. Complete KYC on the exchange
2. Buy USDC with INR (UPI is fastest)
3. Withdraw USDC to your Web3 wallet on the **Arbitrum** network
   - **Do NOT use Ethereum mainnet** — gas fees are $10–30 per transfer
   - Arbitrum fees are pennies
4. Wait for the transfer to confirm (~2 minutes)

### From a global exchange (Binance, Coinbase, etc.):

Same process — withdraw USDC to your wallet on Arbitrum.

---

## Step 3 — Sign Up to Hyperliquid (with my referral)

> 🎁 **Use my referral link to get a 4% lifetime fee discount:**
> **https://app.hyperliquid.xyz/join/REKTCODER**

1. Click the link above
2. Click **Connect Wallet** → choose Rabby or MetaMask
3. Sign the message Hyperliquid asks for (this just proves wallet ownership — it doesn't move funds)
4. You're in

> ⚠️ **The referral must be set BEFORE your first trade.** If you skip this step and trade first, your account is permanently bound to no referrer (or a different one if you somehow connected via someone else's link).

---

## Step 4 — Deposit USDC to Hyperliquid

1. In the Hyperliquid app, click **Deposit**
2. You'll see your Hyperliquid deposit address
3. From your wallet (Rabby/MetaMask), send USDC on **Arbitrum** to that address
4. Wait ~30 seconds. Your USDC will appear in Hyperliquid

**Important:** Hyperliquid auto-bridges Arbitrum USDC to its L1 — that's what the "deposit" flow does. You'll see the balance appear in your Hyperliquid account once confirmed.

---

## Step 5 — Generate an API Wallet

This is CRITICAL for safety. The API wallet (also called "agent") is what your bot will use. **It can trade but cannot withdraw funds.** Even if a hacker steals the API wallet key, they cannot drain your account.

1. In the Hyperliquid app: go to **API** in the menu (or visit [app.hyperliquid.xyz/API](https://app.hyperliquid.xyz/API))
2. Click **Generate API Wallet**
3. Give it a name like "RektCoder Grid Bot"
4. **Copy the private key** when shown — this is the only time you'll see it
5. Save it somewhere secure (1Password, Bitwarden, or encrypted note)

You also need your **main account address** — this is your Web3 wallet's `0x…` address (the one that holds the USDC). You can copy it from Rabby/MetaMask.

---

## Step 6 — Install the Bot

### Install Python 3.10+

If you don't have Python:
- **macOS:** `brew install python@3.11`
- **Windows:** [python.org/downloads](https://python.org/downloads/)
- **Linux:** usually already installed; check with `python3 --version`

### Download the bot

Get it from the **pinned message in [t.me/rektcoderchannel](https://t.me/rektcoderchannel)** — links to the GitHub repo.

```bash
git clone <repo-url>
cd grid_trading_hyperliquid_bot
```

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate         # macOS/Linux
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

---

## Step 7 — Configure the Bot

### Credentials (`.env`)

```bash
cp .env .env
```

Open `.env` in any text editor and fill in:

```
HYPERLIQUID_API_WALLET_PRIVATE_KEY=0xYOUR_API_WALLET_KEY_HERE
HYPERLIQUID_ACCOUNT_ADDRESS=0xYOUR_MAIN_WALLET_ADDRESS_HERE
```

That's the minimum. Telegram alerts are optional — see below.

### Settings (`config.yaml`)

Open `config.yaml` and tune:

```yaml
asset: "BTC"               # What to trade
network: "mainnet"         # mainnet = real money. testnet = paper (free play money)
range_mode: "auto"         # auto picks the range for you
range_pct: 3.0             # auto mode: ±3% from current price
grid_levels: 20            # how many price levels (more = tighter, smaller profits per fill)
capital_usdc: 200.0        # how much USDC to use
leverage: 5                # multiplier — 5x means each $100 controls $500
max_drawdown_pct: 15.0     # auto-pause if equity drops this much
```

### First time? Start with TESTNET

Edit `config.yaml`:
```yaml
network: "testnet"
```

Then visit [app.hyperliquid-testnet.xyz](https://app.hyperliquid-testnet.xyz), connect a (separate) wallet, and use the faucet to get free testnet USDC. Run the bot to make sure everything works before risking real money.

---

## Step 8 — Run the Bot

```bash
python run.py
```

You'll see:
- The banner
- Session info with your network, capital, leverage
- The bot placing initial grid orders
- The live dashboard updating

**Stop cleanly:** press **Ctrl+C**. The bot will cancel all its open grid orders before exiting.

---

## Optional — Telegram Alerts

1. Open Telegram, search **@BotFather**
2. Send `/newbot`, follow prompts, copy the bot token
3. Add your new bot to a channel or group you own
4. Send a message in that channel/group
5. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in a browser
6. Find the `chat.id` (channels start with `-100`)
7. In `.env`:
   ```
   TELEGRAM_BOT_TOKEN=<your bot token>
   TELEGRAM_CHAT_ID=<chat id starting with -100>
   ```
8. In `config.yaml`:
   ```yaml
   telegram_enabled: true
   ```

You'll get alerts on every fill, drawdown breach, and range break.

---

## Troubleshooting

### "Asset 'BTC' not found on Hyperliquid testnet"
Hyperliquid testnet has fewer assets. Try `ETH` or check available assets at [app.hyperliquid-testnet.xyz](https://app.hyperliquid-testnet.xyz).

### "Cannot reach hyperliquid api"
Check internet. If you're in a country that blocks Hyperliquid, you may need a VPN. Hyperliquid is legal in India and most countries, but ISP blocks vary.

### Orders rejected immediately
- Check your capital is enough for the position size (capital × leverage / grid_levels = notional per order)
- Check you have USDC deposited in your **perpetuals** wallet on Hyperliquid (not spot)
- Lower `leverage` if you're under-funded

### Bot says "API wallet does not exist"
You generated the API key but never authorized it. Go back to [app.hyperliquid.xyz/API](https://app.hyperliquid.xyz/API) and click **Authorize**.

### "drawdown breach" — bot paused
That's the safety net firing. Your account dropped by `max_drawdown_pct`. Either:
- Wait for price to recover and the bot resumes automatically
- Stop the bot and review your range / leverage
- Top up your USDC balance

---

## Honest Expectations

This is **not** a money-printer. Realistically:

- **Sideways/choppy markets:** small steady profits (~1–5% / month on capital is realistic)
- **Trending markets:** breakeven to losses (especially in strong dumps)
- **Black swans:** could lose meaningful capital if the range_break safety doesn't trigger in time

The reason to run a grid bot anyway:
- You earn maker rebates on most fills
- You generate volume → unlock referral perks
- You learn how perp DEXes work
- It's mechanical — no panic-trading at 3 AM

**Test on testnet first. Start small on mainnet. Don't bet money you can't lose.**

---

## Support

- 📢 **Telegram:** [t.me/rektcoderchannel](https://t.me/rektcoderchannel) — bot updates, support, community
- ▶ **YouTube:** [@rektcoder](https://youtube.com/@rektcoder) — bot tutorials, deep dives
- 𝕏 **Twitter:** [@rektcoder_](https://twitter.com/rektcoder_)

If this bot helped you, the **single biggest thank you** is signing up to Hyperliquid via my link:

🔗 **https://app.hyperliquid.xyz/join/REKTCODER**

That's how free bots get built and how this channel keeps going. 🙏
