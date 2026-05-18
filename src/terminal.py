"""
═══════════════════════════════════════════════════════════════
  terminal.py — Hedge-fund themed terminal UI (Rich library)
  Built by Tom Hozier · RektCoder
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from rich.align import Align
from rich.box import HEAVY, ROUNDED, SIMPLE_HEAVY
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .brand import (
    BOT_NAME,
    CHANNEL,
    CREATOR,
    NEON_GREEN,
    REFERRAL_URL,
    TELEGRAM,
    TWITTER,
)
from .config import BotConfig
from .state import GridState, ZERO

# Single console instance — shared across the program
console = Console(force_terminal=True, color_system="truecolor")


# ─── color helpers ────────────────────────────────────────────


def neon(text: str) -> Text:
    return Text(text, style=f"bold {NEON_GREEN}")


def dim(text: str) -> Text:
    return Text(text, style="dim")


def fmt_price(p: Decimal, decimals: int = 2) -> str:
    if p == ZERO:
        return "─"
    return f"${float(p):,.{decimals}f}"


def fmt_size(s: Decimal, decimals: int = 6) -> str:
    return f"{float(s):,.{decimals}f}"


def fmt_usd(u: Decimal) -> str:
    return f"${float(u):,.2f}"


def fmt_signed_usd(u: Decimal) -> Text:
    val = float(u)
    if val > 0:
        return Text(f"+${val:,.2f}", style="bold bright_green")
    if val < 0:
        return Text(f"-${abs(val):,.2f}", style="bold bright_red")
    return Text("$0.00", style="dim")


def fmt_pct(p: Decimal) -> Text:
    val = float(p)
    if val > 0:
        return Text(f"+{val:.2f}%", style="bright_green")
    if val < 0:
        return Text(f"{val:.2f}%", style="bright_red")
    return Text(f"{val:.2f}%", style="dim")


def fmt_signed_pct(p: Decimal) -> Text:
    val = float(p)
    if val > 0:
        return Text(f"+{val:.2f}%", style="bold bright_green")
    if val < 0:
        return Text(f"{val:.2f}%", style="bold bright_red")
    return Text("0.00%", style="dim")


def fmt_uptime(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def short_addr(addr: str) -> str:
    if not addr or len(addr) < 12:
        return addr or "─"
    return f"{addr[:6]}…{addr[-4:]}"


# ─── BANNER ───────────────────────────────────────────────────


def print_banner() -> None:
    title = Text()
    title.append("\n")
    title.append("  G R I D   T R A D I N G   H Y P E R L I Q U I D  ", style=f"bold {NEON_GREEN}")
    title.append("\n")
    title.append("                       ", style="")
    title.append("B O T", style="bold white on grey15")
    title.append("\n")

    sub = Text()
    sub.append("Built by ", style="dim italic")
    sub.append(CREATOR, style=f"bold {NEON_GREEN}")
    sub.append(" · ", style="dim")
    sub.append(CHANNEL, style=f"bold {NEON_GREEN}")
    sub.append(" · ", style="dim")
    sub.append(TWITTER, style="bold cyan")

    panel = Panel(
        Align.center(Group(title, Align.center(sub))),
        box=HEAVY,
        border_style=NEON_GREEN,
        padding=(1, 4),
    )
    console.print(panel)


def print_session_info(cfg: BotConfig, account_address: str) -> None:
    net_label = (
        Text("TESTNET", style="bold yellow")
        if cfg.is_testnet
        else Text("MAINNET · LIVE TRADING", style="bold red")
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="dim", no_wrap=True)
    info_table.add_column()

    info_table.add_row("Network", net_label)
    info_table.add_row("Asset", Text(cfg.asset, style="bold bright_white"))
    info_table.add_row("Capital", Text(f"${cfg.capital_usdc:,.2f} USDC", style="bold bright_green"))
    info_table.add_row("Leverage", Text(f"{cfg.leverage}x", style="bold bright_yellow"))
    info_table.add_row("Account", Text(short_addr(account_address), style="bright_blue"))
    info_table.add_row("Started", Text(timestamp, style="white"))

    ref_table = Table.grid(padding=(0, 2))
    ref_table.add_column(style=f"bold {NEON_GREEN}", no_wrap=True)
    ref_table.add_column()
    ref_table.add_row("REKTCODER REF", Text(REFERRAL_URL, style="italic cyan"))
    ref_table.add_row("Telegram", Text(TELEGRAM, style="italic cyan"))

    inner = Group(
        info_table,
        Text(""),
        Panel(ref_table, box=ROUNDED, border_style=NEON_GREEN, padding=(0, 1)),
    )

    console.print(Panel(inner, title="[bold]SESSION[/]", box=HEAVY, border_style=NEON_GREEN))


# ─── DASHBOARD BUILDERS ───────────────────────────────────────


def _market_panel(state: GridState) -> Panel:
    t = Table.grid(padding=(0, 3))
    t.add_column(style="dim", no_wrap=True)
    t.add_column(no_wrap=True)
    t.add_column(style="dim", no_wrap=True)
    t.add_column(no_wrap=True)

    t.add_row(
        "Mid Price",
        Text(fmt_price(state.mid_price), style="bold bright_white"),
        "24h Change",
        fmt_pct(state.h24_change_pct),
    )
    t.add_row(
        "Best Bid",
        Text(fmt_price(state.best_bid), style="bright_green"),
        "Best Ask",
        Text(fmt_price(state.best_ask), style="bright_red"),
    )
    return Panel(t, title="[bold]MARKET[/]", box=ROUNDED, border_style="bright_cyan")


def _grid_panel(state: GridState, cfg: BotConfig) -> Panel:
    info = Table.grid(padding=(0, 3))
    info.add_column(style="dim", no_wrap=True)
    info.add_column(no_wrap=True)
    info.add_column(style="dim", no_wrap=True)
    info.add_column(no_wrap=True)
    info.add_row(
        "Levels",
        Text(str(cfg.grid_levels), style="bright_white"),
        "Spacing",
        Text(fmt_price(state.grid_spacing), style="bright_white"),
    )
    info.add_row(
        "Lower",
        Text(fmt_price(state.range_lower), style="bright_yellow"),
        "Upper",
        Text(fmt_price(state.range_upper), style="bright_yellow"),
    )

    ladder = Table(box=SIMPLE_HEAVY, show_header=True, header_style="bold dim", expand=True)
    ladder.add_column("Status", justify="center", width=8)
    ladder.add_column("Side", justify="center", width=6)
    ladder.add_column("Price", justify="right", width=14)
    ladder.add_column("Size", justify="right", width=12)
    ladder.add_column("Fills", justify="right", width=6)
    ladder.add_column("OID", justify="left", width=10, style="dim")

    sorted_orders = sorted(
        state.grid_orders.values(), key=lambda o: o.price, reverse=True
    )
    half_spacing = state.grid_spacing / Decimal("2") if state.grid_spacing > ZERO else ZERO

    for order in sorted_orders:
        status_style = {
            "open": "bright_cyan",
            "filled": "bold bright_yellow",
            "cancelled": "dim",
            "pending": "dim italic",
        }.get(order.status, "white")

        side_text = (
            Text("BUY", style="bold bright_green")
            if order.is_buy
            else Text("SELL", style="bold bright_red")
        )
        status_text = Text(order.status.upper(), style=status_style)
        price_text = Text(fmt_price(order.price), style="white")
        near_mid = (
            abs(order.price - state.mid_price) <= half_spacing if state.mid_price > ZERO else False
        )
        if near_mid:
            price_text = Text(fmt_price(order.price) + " ←", style="bold bright_white on grey15")

        ladder.add_row(
            status_text,
            side_text,
            price_text,
            Text(fmt_size(order.size, 6), style="dim"),
            Text(str(order.fill_count), style="bright_white"),
            order.client_oid_short,
        )

    return Panel(
        Group(info, Text(""), ladder),
        title="[bold]GRID LADDER[/]",
        box=ROUNDED,
        border_style=NEON_GREEN,
    )


def _position_panel(state: GridState, cfg: BotConfig) -> Panel:
    t = Table.grid(padding=(0, 3))
    t.add_column(style="dim", no_wrap=True)
    t.add_column(no_wrap=True)
    t.add_column(style="dim", no_wrap=True)
    t.add_column(no_wrap=True)

    if state.net_position_size > ZERO:
        side_str = Text(f"+{fmt_size(state.net_position_size)} {cfg.asset}", style="bright_green")
    elif state.net_position_size < ZERO:
        side_str = Text(f"{fmt_size(state.net_position_size)} {cfg.asset}", style="bright_red")
    else:
        side_str = Text("FLAT", style="dim")

    t.add_row(
        "Net Position",
        side_str,
        "Avg Entry",
        Text(fmt_price(state.avg_entry_price), style="bright_white"),
    )
    t.add_row(
        "Unrealized P&L",
        fmt_signed_usd(state.unrealized_pnl),
        "Return",
        fmt_signed_pct(state.unrealized_pnl_pct),
    )
    return Panel(t, title="[bold]POSITION[/]", box=ROUNDED, border_style="bright_blue")


def _pnl_panel(state: GridState) -> Panel:
    t = Table.grid(padding=(0, 3))
    t.add_column(style="dim", no_wrap=True)
    t.add_column(no_wrap=True)
    t.add_column(style="dim", no_wrap=True)
    t.add_column(no_wrap=True)

    t.add_row(
        "Fills",
        Text(f"{state.total_fills}", style="bold bright_white"),
        "Volume",
        Text(fmt_usd(state.total_volume_usd), style="bright_white"),
    )
    t.add_row(
        "Realized P&L",
        fmt_signed_usd(state.realized_pnl),
        "Maker Rebates",
        fmt_signed_usd(state.maker_rebates_total),
    )
    t.add_row(
        "Drawdown",
        Text(f"-{float(state.current_drawdown_pct):.2f}%", style="bright_red" if state.current_drawdown_pct > ZERO else "dim"),
        "Uptime",
        Text(fmt_uptime(state.uptime_seconds), style="dim"),
    )
    t.add_row(
        "Equity",
        Text(fmt_usd(state.current_equity), style="bold bright_white"),
        "Peak",
        Text(fmt_usd(state.peak_equity), style="bright_yellow"),
    )
    return Panel(t, title="[bold]SESSION P&L[/]", box=ROUNDED, border_style="bright_magenta")


def build_dashboard(state: GridState, cfg: BotConfig) -> Layout:
    """Compose the full hedge-fund themed dashboard layout."""
    layout = Layout()
    # Give the grid ladder the largest section since it has the most info
    layout.split_column(
        Layout(name="top", size=6),
        Layout(name="middle", ratio=2, minimum_size=14),
        Layout(name="bottom", size=8),
    )
    layout["top"].split_row(
        Layout(_market_panel(state), name="market"),
        Layout(_position_panel(state, cfg), name="position"),
    )
    layout["middle"].update(_grid_panel(state, cfg))
    layout["bottom"].update(_pnl_panel(state))
    return layout


# ─── EVENT LOGS (always visible above the live region) ────────


def print_fill_event(side: str, price: Decimal, size: Decimal, asset: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    side_tag = (
        Text(" BUY  ", style="bold black on bright_green")
        if side == "buy"
        else Text(" SELL ", style="bold white on bright_red")
    )
    line = Text()
    line.append(f"[{ts}] ", style="dim")
    line.append("FILL  ", style=f"bold {NEON_GREEN}")
    line.append(side_tag)
    line.append(f"  {fmt_size(size)} ", style="bold bright_white")
    line.append(f"@ {fmt_price(price)} ", style="bold bright_white")
    line.append(asset, style="dim")
    console.print(line)


def print_alert(severity: str, msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    tag_map = {
        "critical": Text(" CRITICAL ", style="bold white on red"),
        "warn": Text("   WARN   ", style="bold black on yellow"),
        "info": Text("   INFO   ", style="bold black on cyan"),
        "ok": Text("    OK    ", style=f"bold black on {NEON_GREEN}"),
    }
    tag = tag_map.get(severity, Text("          "))
    line = Text()
    line.append(f"[{ts}] ", style="dim")
    line.append(tag)
    line.append("  ")
    line.append(msg, style="bright_white")
    console.print(line)


def print_info(msg: str) -> None:
    print_alert("info", msg)
