"""
═══════════════════════════════════════════════════════════════
  state.py — In-memory bot state (orders, positions, P&L)
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

ZERO = Decimal("0")
HUNDRED = Decimal("100")
MAKER_REBATE_RATE = Decimal("0.00015")  # Hyperliquid effective maker rebate


def _rand_suffix() -> str:
    return f"{int(time.time() * 1e6) & 0xFFFFFF:06x}"


def _new_oid() -> str:
    return f"rk-{int(time.time() * 1000)}-{_rand_suffix()}"


@dataclass
class OrderState:
    price: Decimal
    size: Decimal
    is_buy: bool
    client_oid: str = field(default_factory=_new_oid)
    exchange_oid: Optional[int] = None
    status: str = "pending"           # pending | open | filled | cancelled
    fill_count: int = 0
    placed_at: int = field(default_factory=lambda: int(time.time()))
    last_fill_at: Optional[int] = None

    @property
    def client_oid_short(self) -> str:
        return self.client_oid[-6:]

    @property
    def side(self) -> str:
        return "buy" if self.is_buy else "sell"


@dataclass
class GridState:
    starting_equity: Decimal

    # Market
    mid_price: Decimal = ZERO
    best_bid: Decimal = ZERO
    best_ask: Decimal = ZERO
    h24_change_pct: Decimal = ZERO

    # Grid
    range_lower: Decimal = ZERO
    range_upper: Decimal = ZERO
    grid_spacing: Decimal = ZERO
    grid_orders: dict[str, OrderState] = field(default_factory=dict)

    # Position
    net_position_size: Decimal = ZERO   # +long, -short
    avg_entry_price: Decimal = ZERO
    unrealized_pnl: Decimal = ZERO
    unrealized_pnl_pct: Decimal = ZERO

    # Session stats
    total_fills: int = 0
    total_volume_usd: Decimal = ZERO
    realized_pnl: Decimal = ZERO
    maker_rebates_total: Decimal = ZERO
    current_drawdown_pct: Decimal = ZERO
    peak_equity: Decimal = ZERO
    started_at: int = field(default_factory=lambda: int(time.time()))

    def __post_init__(self) -> None:
        self.peak_equity = self.starting_equity

    @property
    def current_equity(self) -> Decimal:
        return self.starting_equity + self.realized_pnl + self.unrealized_pnl

    @property
    def uptime_seconds(self) -> int:
        return max(0, int(time.time()) - self.started_at)

    def record_fill(self, is_buy: bool, price: Decimal, size: Decimal, is_maker: bool) -> None:
        self.total_fills += 1
        notional = price * size
        self.total_volume_usd += notional

        if is_maker:
            self.maker_rebates_total += notional * MAKER_REBATE_RATE

        delta = size if is_buy else -size

        # Weighted-average accounting
        same_side = (
            self.net_position_size == ZERO
            or (self.net_position_size > 0 and delta > 0)
            or (self.net_position_size < 0 and delta < 0)
        )
        if same_side:
            prev_notional = self.avg_entry_price * abs(self.net_position_size)
            total_notional = prev_notional + (price * size)
            total_size = abs(self.net_position_size) + size
            if total_size > ZERO:
                self.avg_entry_price = total_notional / total_size
        else:
            # Closing or flipping — realize P&L on closed portion
            closing_size = min(size, abs(self.net_position_size))
            if self.net_position_size > 0:
                direction = price - self.avg_entry_price
            else:
                direction = self.avg_entry_price - price
            self.realized_pnl += direction * closing_size
            # If we flipped through zero, reset avg entry on remainder
            if size > abs(self.net_position_size):
                self.avg_entry_price = price

        self.net_position_size = self.net_position_size + delta
        if self.net_position_size == ZERO:
            self.avg_entry_price = ZERO

        # Drawdown tracking
        eq = self.current_equity
        if eq > self.peak_equity:
            self.peak_equity = eq
        if self.peak_equity > ZERO:
            self.current_drawdown_pct = (
                (self.peak_equity - eq) / self.peak_equity * HUNDRED
            )

    def update_unrealized(self) -> None:
        if self.net_position_size == ZERO or self.avg_entry_price == ZERO:
            self.unrealized_pnl = ZERO
            self.unrealized_pnl_pct = ZERO
            return
        if self.net_position_size > 0:
            direction = self.mid_price - self.avg_entry_price
        else:
            direction = self.avg_entry_price - self.mid_price
        self.unrealized_pnl = direction * abs(self.net_position_size)
        cost_basis = self.avg_entry_price * abs(self.net_position_size)
        if cost_basis > ZERO:
            self.unrealized_pnl_pct = self.unrealized_pnl / cost_basis * HUNDRED
