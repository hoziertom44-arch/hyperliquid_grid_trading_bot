"""
═══════════════════════════════════════════════════════════════
  trade_log.py — JSONL trade journal (append-only)
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any


def _default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not JSON serializable")


def append(path: str | Path, record: dict[str, Any]) -> None:
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    line = json.dumps(record, default=_default)
    with open(path, "a") as f:
        f.write(line + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
