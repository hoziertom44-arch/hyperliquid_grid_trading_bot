"""
═══════════════════════════════════════════════════════════════
  main.py — Entry point
  Built by Tom Hozier · RektCoder
  https://app.hyperliquid.xyz/join/REKTCODER
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import sys

from .bot import GridBot
from .config import load_config, load_env
from .hyperliquid_client import HyperliquidClient
from .telegram import TelegramAlerter
from .terminal import console, print_alert, print_banner, print_session_info


def main() -> int:
    print_banner()

    # Load config
    try:
        cfg = load_config()
    except Exception as e:
        print_alert("critical", f"Config error: {e}")
        return 1

    # Load credentials
    try:
        secrets = load_env()
    except Exception as e:
        print_alert("critical", f"Credential error: {e}")
        print_alert("info", "Copy .env to .env and fill in your Hyperliquid keys.")
        return 1

    print_session_info(cfg, secrets.account_address)

    # Connect to Hyperliquid
    try:
        client = HyperliquidClient(cfg, secrets)
    except Exception as e:
        print_alert("critical", f"Hyperliquid connection failed: {e}")
        return 1

    # Telegram (optional)
    alerter = TelegramAlerter(
        enabled=cfg.telegram_enabled,
        bot_token=secrets.telegram_bot_token,
        chat_id=secrets.telegram_chat_id,
    )
    if alerter.enabled:
        print_alert("ok", "Telegram alerts enabled")

    bot = GridBot(cfg, client, alerter)

    # Initialize grid
    try:
        bot.initialize()
    except Exception as e:
        print_alert("critical", f"Bootstrap failed: {e}")
        try:
            bot.shutdown()
        except Exception:
            pass
        return 1

    print_alert("ok", "Grid armed. Ctrl+C to stop cleanly.")
    console.print()

    # Run forever
    try:
        bot.run()
    except KeyboardInterrupt:
        console.print()
        print_alert("info", "Ctrl+C received")
    except Exception as e:
        print_alert("critical", f"Unexpected error: {e}")
    finally:
        try:
            bot.shutdown()
        except Exception as e:
            print_alert("warn", f"Shutdown error: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
