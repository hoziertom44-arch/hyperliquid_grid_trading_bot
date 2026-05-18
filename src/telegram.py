"""
═══════════════════════════════════════════════════════════════
  telegram.py — Optional Telegram alerts
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import requests


class TelegramAlerter:
    def __init__(
        self,
        enabled: bool,
        bot_token: str | None,
        chat_id: str | None,
    ) -> None:
        self.enabled = bool(enabled and bot_token and chat_id)
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, text: str) -> None:
        if not self.enabled:
            return
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            requests.post(
                url,
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=8,
            )
        except Exception:
            # Never let alerting break the bot
            pass
