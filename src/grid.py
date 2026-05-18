"""
═══════════════════════════════════════════════════════════════
  grid.py — Pure grid trading math
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from .config import BotConfig
from .state import OrderState, ZERO

ONE = Decimal("1")
TWO = Decimal("2")
HUNDRED = Decimal("100")


@dataclass
class GridPlan:
    range_lower: Decimal
    range_upper: Decimal
    spacing: Decimal
    levels: list[Decimal]       # sorted ascending
    size_per_level: Decimal     # base asset units per level


def build_plan(cfg: BotConfig, current_price: Decimal) -> GridPlan:
    """Build a grid plan from config + current price."""
    if cfg.range_mode == "auto":
        pct = Decimal(str(cfg.range_pct)) / HUNDRED
        lower = current_price * (ONE - pct)
        upper = current_price * (ONE + pct)
    else:
        lower = Decimal(str(cfg.range_lower))
        upper = Decimal(str(cfg.range_upper))

    spacing = (upper - lower) / Decimal(cfg.grid_levels)

    levels: list[Decimal] = []
    for i in range(cfg.grid_levels + 1):
        levels.append(lower + spacing * Decimal(i))

    mid_for_sizing = (lower + upper) / TWO
    if mid_for_sizing > ZERO:
        size_per_level = cfg.capital_per_level_notional / mid_for_sizing
    else:
        size_per_level = ZERO

    return GridPlan(
        range_lower=lower,
        range_upper=upper,
        spacing=spacing,
        levels=levels,
        size_per_level=size_per_level,
    )


def initial_orders(plan: GridPlan, mid_price: Decimal) -> List[OrderState]:
    """Generate initial buy-below / sell-above orders."""
    orders: list[OrderState] = []
    for level in plan.levels:
        # Skip the level closest to mid — would fill immediately
        if abs(level - mid_price) < plan.spacing / TWO:
            continue
        is_buy = level < mid_price
        orders.append(OrderState(price=level, size=plan.size_per_level, is_buy=is_buy))
    return orders


def replacement_order(filled: OrderState, spacing: Decimal) -> OrderState:
    """When a grid order fills, place an opposite-side order one level away."""
    if filled.is_buy:
        new_price = filled.price + spacing
        return OrderState(price=new_price, size=filled.size, is_buy=False)
    new_price = filled.price - spacing
    return OrderState(price=new_price, size=filled.size, is_buy=True)


def is_range_broken(mid: Decimal, plan: GridPlan, break_pct: float) -> bool:
    """Has price exited the grid range by more than break_pct?"""
    pct = Decimal(str(break_pct)) / HUNDRED
    return mid < plan.range_lower * (ONE - pct) or mid > plan.range_upper * (ONE + pct)
