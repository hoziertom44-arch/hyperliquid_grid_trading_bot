"""
═══════════════════════════════════════════════════════════════
  hyperliquid_client.py — Official SDK wrapper
  Built by Tom Hozier · RektCoder
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import eth_account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

from .config import BotConfig, EnvSecrets


@dataclass
class OpenOrderInfo:
    asset: str
    oid: int
    price: Decimal
    size: Decimal
    is_buy: bool


class HyperliquidClient:
    """Thin async-friendly wrapper around the official Hyperliquid SDK."""

    def __init__(self, cfg: BotConfig, secrets: EnvSecrets) -> None:
        self.cfg = cfg
        self.secrets = secrets
        base_url = (
            constants.TESTNET_API_URL if cfg.is_testnet else constants.MAINNET_API_URL
        )
        self.info = Info(base_url, skip_ws=True)
        wallet = eth_account.Account.from_key(secrets.api_wallet_private_key)
        self.exchange = Exchange(wallet, base_url, account_address=secrets.account_address)

        # Cache asset metadata (sz_decimals) so we can round sizes correctly
        meta = self.info.meta()
        self._sz_decimals: dict[str, int] = {}
        self._asset_index: dict[str, int] = {}
        for idx, asset_meta in enumerate(meta.get("universe", [])):
            self._sz_decimals[asset_meta["name"]] = int(asset_meta.get("szDecimals", 4))
            self._asset_index[asset_meta["name"]] = idx
        if cfg.asset not in self._sz_decimals:
            raise ValueError(
                f"Asset '{cfg.asset}' not found on Hyperliquid {cfg.network}. "
                f"Available: {sorted(self._sz_decimals)[:20]}…"
            )

    # ─── ROUNDING HELPERS ────────────────────────────────────

    def round_size(self, size: Decimal) -> float:
        decimals = self._sz_decimals.get(self.cfg.asset, 4)
        # Convert to float at the right precision
        quant = Decimal(10) ** (-decimals)
        rounded = size.quantize(quant)
        return float(rounded)

    def round_price(self, price: Decimal) -> float:
        """Hyperliquid: prices have up to 5 significant figures, max 6 decimals for perps."""
        f = float(price)
        if f == 0:
            return 0.0
        # 5 significant figures
        from decimal import Decimal as D
        from math import log10, floor
        magnitude = floor(log10(abs(f)))
        decimals = max(0, min(6, 4 - magnitude))
        rounded = round(f, decimals)
        return rounded

    # ─── MARKET DATA ─────────────────────────────────────────

    def get_mid_price(self) -> Decimal:
        mids = self.info.all_mids()
        raw = mids.get(self.cfg.asset)
        if raw is None:
            raise RuntimeError(
                f"Mid price for {self.cfg.asset} not returned (check asset name on this network)."
            )
        return Decimal(str(raw))

    def get_top_of_book(self) -> tuple[Decimal, Decimal]:
        try:
            snap = self.info.l2_snapshot(self.cfg.asset)
            # snap["levels"] = [[bids...], [asks...]]
            levels = snap.get("levels", [[], []])
            best_bid = Decimal("0")
            best_ask = Decimal("0")
            if levels and levels[0]:
                best_bid = Decimal(str(levels[0][0]["px"]))
            if len(levels) > 1 and levels[1]:
                best_ask = Decimal(str(levels[1][0]["px"]))
            return best_bid, best_ask
        except Exception:
            return Decimal("0"), Decimal("0")

    def get_24h_change_pct(self) -> Decimal:
        try:
            meta_and_ctxs = self.info.meta_and_asset_ctxs()
            if not isinstance(meta_and_ctxs, list) or len(meta_and_ctxs) < 2:
                return Decimal("0")
            ctxs = meta_and_ctxs[1]
            idx = self._asset_index.get(self.cfg.asset)
            if idx is None or idx >= len(ctxs):
                return Decimal("0")
            ctx = ctxs[idx]
            prev = Decimal(str(ctx.get("prevDayPx", "0")))
            mark = Decimal(str(ctx.get("markPx", "0")))
            if prev > 0:
                return (mark - prev) / prev * Decimal("100")
            return Decimal("0")
        except Exception:
            return Decimal("0")

    # ─── ORDERS ──────────────────────────────────────────────

    def place_limit_order(
        self,
        price: Decimal,
        size: Decimal,
        is_buy: bool,
        post_only: bool,
        time_in_force: str,
        reduce_only: bool = False,
    ) -> Optional[int]:
        """Place a single limit order. Returns the exchange order id or None."""
        tif = "Alo" if post_only else time_in_force  # Alo = Add Liquidity Only = post-only
        order_type = {"limit": {"tif": tif}}
        result = self.exchange.order(
            self.cfg.asset,
            is_buy,
            self.round_size(size),
            self.round_price(price),
            order_type,
            reduce_only=reduce_only,
        )
        if result.get("status") != "ok":
            return None
        try:
            statuses = result["response"]["data"]["statuses"]
            if not statuses:
                return None
            status = statuses[0]
            if "resting" in status:
                return int(status["resting"]["oid"])
            if "filled" in status:
                return int(status["filled"].get("oid", 0)) or None
            # "error" key means rejection (e.g. post-only would have crossed)
            return None
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def cancel_order(self, oid: int) -> bool:
        try:
            res = self.exchange.cancel(self.cfg.asset, oid)
            return res.get("status") == "ok"
        except Exception:
            return False

    def get_open_orders(self) -> list[OpenOrderInfo]:
        try:
            raw = self.info.open_orders(self.secrets.account_address)
        except Exception:
            return []
        out: list[OpenOrderInfo] = []
        for o in raw or []:
            if o.get("coin") != self.cfg.asset:
                continue
            try:
                out.append(
                    OpenOrderInfo(
                        asset=o["coin"],
                        oid=int(o["oid"]),
                        price=Decimal(str(o["limitPx"])),
                        size=Decimal(str(o["sz"])),
                        is_buy=(o.get("side") == "B"),
                    )
                )
            except (KeyError, ValueError):
                continue
        return out

    def get_position_size(self) -> Decimal:
        """Returns signed position size for the configured asset (+long, -short, 0 flat)."""
        try:
            state = self.info.user_state(self.secrets.account_address)
        except Exception:
            return Decimal("0")
        for ap in state.get("assetPositions", []):
            pos = ap.get("position", {})
            if pos.get("coin") == self.cfg.asset:
                szi = pos.get("szi", "0")
                return Decimal(str(szi))
        return Decimal("0")
