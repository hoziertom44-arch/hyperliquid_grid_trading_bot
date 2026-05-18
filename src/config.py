"""
═══════════════════════════════════════════════════════════════
  config.py — Configuration & secrets loader
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class BotConfig:
    asset: str
    network: str

    range_mode: str
    range_pct: float
    range_lower: float
    range_upper: float
    grid_levels: int

    capital_usdc: float
    leverage: int
    max_drawdown_pct: float
    range_break_pct: float

    post_only: bool
    time_in_force: str

    refresh_interval_seconds: int
    verbose_logging: bool
    persist_trades: bool
    trades_log_file: str

    telegram_enabled: bool
    telegram_alert_on_fill: bool
    telegram_alert_on_range_break: bool
    telegram_alert_on_drawdown: bool

    @property
    def is_testnet(self) -> bool:
        return self.network == "testnet"

    @property
    def capital_per_level_notional(self) -> Decimal:
        return (
            Decimal(str(self.capital_usdc)) * Decimal(self.leverage)
        ) / Decimal(self.grid_levels)


@dataclass
class EnvSecrets:
    api_wallet_private_key: str
    account_address: str
    telegram_bot_token: str | None
    telegram_chat_id: str | None


def load_config(path: Path | None = None) -> BotConfig:
    cfg_path = path or (PROJECT_ROOT / "config.yaml")
    if not cfg_path.exists():
        raise FileNotFoundError(f"config.yaml not found at {cfg_path}")
    with open(cfg_path) as f:
        raw = yaml.safe_load(f)

    cfg = BotConfig(
        asset=str(raw["asset"]).strip().upper(),
        network=str(raw["network"]).strip().lower(),
        range_mode=str(raw["range_mode"]).strip().lower(),
        range_pct=float(raw["range_pct"]),
        range_lower=float(raw["range_lower"]),
        range_upper=float(raw["range_upper"]),
        grid_levels=int(raw["grid_levels"]),
        capital_usdc=float(raw["capital_usdc"]),
        leverage=int(raw["leverage"]),
        max_drawdown_pct=float(raw["max_drawdown_pct"]),
        range_break_pct=float(raw["range_break_pct"]),
        post_only=bool(raw["post_only"]),
        time_in_force=str(raw.get("time_in_force", "Gtc")),
        refresh_interval_seconds=int(raw["refresh_interval_seconds"]),
        verbose_logging=bool(raw["verbose_logging"]),
        persist_trades=bool(raw["persist_trades"]),
        trades_log_file=str(raw["trades_log_file"]),
        telegram_enabled=bool(raw.get("telegram_enabled", False)),
        telegram_alert_on_fill=bool(raw.get("telegram_alert_on_fill", True)),
        telegram_alert_on_range_break=bool(raw.get("telegram_alert_on_range_break", True)),
        telegram_alert_on_drawdown=bool(raw.get("telegram_alert_on_drawdown", True)),
    )
    _validate(cfg)
    return cfg


def _validate(cfg: BotConfig) -> None:
    if cfg.network not in ("mainnet", "testnet"):
        raise ValueError("network must be 'mainnet' or 'testnet'")
    if cfg.range_mode not in ("auto", "manual"):
        raise ValueError("range_mode must be 'auto' or 'manual'")
    if not (4 <= cfg.grid_levels <= 100):
        raise ValueError("grid_levels must be between 4 and 100")
    if cfg.capital_usdc < 10:
        raise ValueError("capital_usdc must be at least 10")
    if not (1 <= cfg.leverage <= 40):
        raise ValueError("leverage must be between 1 and 40 on Hyperliquid")
    if cfg.range_pct <= 0 or cfg.range_pct > 50:
        raise ValueError("range_pct must be between 0 and 50")
    if cfg.range_mode == "manual" and cfg.range_lower >= cfg.range_upper:
        raise ValueError("range_lower must be less than range_upper")


def load_env(path: Path | None = None) -> EnvSecrets:
    env_path = path or (PROJECT_ROOT / ".env")
    load_dotenv(env_path)

    api_key = (os.getenv("HYPERLIQUID_API_WALLET_PRIVATE_KEY") or "").strip()
    if not api_key or api_key.startswith("0x_paste"):
        raise ValueError(
            "HYPERLIQUID_API_WALLET_PRIVATE_KEY not set. Copy .env to .env and fill it in."
        )
    if not api_key.startswith("0x"):
        api_key = "0x" + api_key

    address = (os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS") or "").strip()
    if not address or address.startswith("0x_paste"):
        raise ValueError(
            "HYPERLIQUID_ACCOUNT_ADDRESS not set. Paste your main wallet address in .env."
        )
    if not address.startswith("0x") or len(address) < 40:
        raise ValueError("HYPERLIQUID_ACCOUNT_ADDRESS must be a valid 0x… address.")

    tg_token = os.getenv("TELEGRAM_BOT_TOKEN") or None
    tg_chat = os.getenv("TELEGRAM_CHAT_ID") or None
    if tg_token == "":
        tg_token = None
    if tg_chat == "":
        tg_chat = None

    return EnvSecrets(
        api_wallet_private_key=api_key,
        account_address=address,
        telegram_bot_token=tg_token,
        telegram_chat_id=tg_chat,
    )
