"""
═══════════════════════════════════════════════════════════════
  risk.py — Risk management & safety circuit breakers
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

from .config import BotConfig
from .state import GridState, ZERO


class RiskVerdict(Enum):
    OK = "ok"
    PAUSE_DRAWDOWN = "pause_drawdown"
    PAUSE_RANGE_BREAK = "pause_range_break"

    @property
    def should_pause(self) -> bool:
        return self != RiskVerdict.OK


def evaluate(state: GridState, cfg: BotConfig) -> RiskVerdict:
    # 1. Drawdown
    if state.current_drawdown_pct >= Decimal(str(cfg.max_drawdown_pct)):
        return RiskVerdict.PAUSE_DRAWDOWN

    # 2. Range break
    break_pct = Decimal(str(cfg.range_break_pct)) / Decimal("100")
    if state.mid_price > ZERO and state.range_lower > ZERO and state.range_upper > ZERO:
        break_below = state.range_lower * (Decimal("1") - break_pct)
        break_above = state.range_upper * (Decimal("1") + break_pct)
        if state.mid_price < break_below or state.mid_price > break_above:
            return RiskVerdict.PAUSE_RANGE_BREAK

    return RiskVerdict.OK
