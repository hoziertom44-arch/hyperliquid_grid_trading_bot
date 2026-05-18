"""
═══════════════════════════════════════════════════════════════
  bot.py — Main grid trading loop
  Built by Tom Hozier · RektCoder
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import time
from decimal import Decimal

from rich.live import Live

from . import grid, risk, trade_log
from .config import BotConfig
from .hyperliquid_client import HyperliquidClient
from .state import GridState, OrderState, ZERO
from .telegram import TelegramAlerter
from .terminal import (
    build_dashboard,
    console,
    print_alert,
    print_fill_event,
    print_info,
)


class GridBot:
    def __init__(
        self,
        cfg: BotConfig,
        client: HyperliquidClient,
        alerter: TelegramAlerter,
    ) -> None:
        self.cfg = cfg
        self.client = client
        self.alerter = alerter
        self.state = GridState(starting_equity=Decimal(str(cfg.capital_usdc)))
        self.plan: grid.GridPlan | None = None
        self._paused = False
        self._pause_reason: str | None = None

    # ─── BOOTSTRAP ────────────────────────────────────────────

    def initialize(self) -> None:
        print_info(f"Connecting to Hyperliquid {self.cfg.network}…")
        mid = self.client.get_mid_price()
        self.state.mid_price = mid
        print_alert("ok", f"Mid price for {self.cfg.asset}: ${float(mid):,.2f}")

        plan = grid.build_plan(self.cfg, mid)
        self.state.range_lower = plan.range_lower
        self.state.range_upper = plan.range_upper
        self.state.grid_spacing = plan.spacing
        self.plan = plan

        print_info(
            f"Grid: ${float(plan.range_lower):,.2f} — ${float(plan.range_upper):,.2f} "
            f"with {self.cfg.grid_levels} levels (spacing ${float(plan.spacing):,.2f})"
        )

        if self.alerter.enabled:
            self.alerter.send(
                f"🤖 <b>Grid Bot started</b>\n"
                f"Asset: <b>{self.cfg.asset}</b>\n"
                f"Mid: <b>${float(mid):,.2f}</b>\n"
                f"Range: ${float(plan.range_lower):,.2f} — ${float(plan.range_upper):,.2f}\n"
                f"Levels: {self.cfg.grid_levels}\n"
                f"Capital: ${self.cfg.capital_usdc:,.2f} ({self.cfg.leverage}x)\n\n"
                f"<i>Built by Tom Hozier · @rektcoder_</i>"
            )

        initial = grid.initial_orders(plan, mid)
        print_info(f"Placing {len(initial)} grid orders…")
        for order in initial:
            self._place(order)
            time.sleep(0.12)  # gentle throttle
        print_alert("ok", f"Grid active with {len(self.state.grid_orders)} open orders")

    # ─── ORDER PLACEMENT ─────────────────────────────────────

    def _place(self, order: OrderState) -> None:
        oid = self.client.place_limit_order(
            price=order.price,
            size=order.size,
            is_buy=order.is_buy,
            post_only=self.cfg.post_only,
            time_in_force=self.cfg.time_in_force,
            reduce_only=False,
        )
        if oid is None:
            print_alert(
                "warn",
                f"Order rejected: {order.side.upper()} {float(order.size):.6f} @ ${float(order.price):,.2f}",
            )
            order.status = "cancelled"
            self.state.grid_orders[order.client_oid] = order
            return

        order.exchange_oid = oid
        order.status = "open"
        self.state.grid_orders[order.client_oid] = order

        if self.cfg.persist_trades:
            trade_log.append(
                self.cfg.trades_log_file,
                {
                    "event": "place",
                    "asset": self.cfg.asset,
                    "side": order.side,
                    "price": order.price,
                    "size": order.size,
                    "client_oid": order.client_oid,
                    "exchange_oid": oid,
                },
            )

    # ─── MAIN TICK ───────────────────────────────────────────

    def tick(self) -> None:
        # 1. Refresh market data
        try:
            self.state.mid_price = self.client.get_mid_price()
        except Exception as e:
            print_alert("warn", f"mid_price fetch failed: {e}")

        bid, ask = self.client.get_top_of_book()
        if bid > ZERO:
            self.state.best_bid = bid
        if ask > ZERO:
            self.state.best_ask = ask

        self.state.h24_change_pct = self.client.get_24h_change_pct()

        # 2. Reconcile open orders with exchange
        exch_orders = self.client.get_open_orders()
        exch_oids = {o.oid for o in exch_orders}

        filled_to_replace: list[OrderState] = []
        for cloid, order in list(self.state.grid_orders.items()):
            if order.status != "open" or order.exchange_oid is None:
                continue
            if order.exchange_oid not in exch_oids:
                # No longer open on exchange → assume filled
                order.status = "filled"
                order.fill_count += 1
                order.last_fill_at = int(time.time())
                self.state.record_fill(
                    is_buy=order.is_buy,
                    price=order.price,
                    size=order.size,
                    is_maker=self.cfg.post_only,
                )

                print_fill_event(order.side, order.price, order.size, self.cfg.asset)

                if self.cfg.persist_trades:
                    trade_log.append(
                        self.cfg.trades_log_file,
                        {
                            "event": "fill",
                            "asset": self.cfg.asset,
                            "side": order.side,
                            "price": order.price,
                            "size": order.size,
                            "client_oid": order.client_oid,
                            "exchange_oid": order.exchange_oid,
                            "fill_count": order.fill_count,
                        },
                    )

                if self.cfg.telegram_alert_on_fill:
                    self.alerter.send(
                        f"🟢 <b>FILL</b> {order.side.upper()} {float(order.size):.6f} {self.cfg.asset} "
                        f"@ ${float(order.price):,.2f}\nSession fills: {self.state.total_fills}"
                    )

                filled_to_replace.append(order)

        # 3. Replace filled orders
        if self.plan and not self._paused:
            for filled in filled_to_replace:
                repl = grid.replacement_order(filled, self.plan.spacing)
                self._place(repl)
                time.sleep(0.1)

        # 4. Update unrealized P&L
        self.state.update_unrealized()

        # 5. Risk check
        verdict = risk.evaluate(self.state, self.cfg)
        if verdict.should_pause:
            if not self._paused or self._pause_reason != verdict.value:
                self._paused = True
                self._pause_reason = verdict.value
                if verdict == risk.RiskVerdict.PAUSE_DRAWDOWN:
                    msg = f"DRAWDOWN BREACH ({float(self.state.current_drawdown_pct):.2f}%). Pausing new orders."
                    print_alert("critical", msg)
                    if self.cfg.telegram_alert_on_drawdown:
                        self.alerter.send(
                            f"🚨 <b>DRAWDOWN BREACH</b>\n"
                            f"Current: {float(self.state.current_drawdown_pct):.2f}%\n"
                            f"Max: {self.cfg.max_drawdown_pct}%\n"
                            f"Bot paused."
                        )
                elif verdict == risk.RiskVerdict.PAUSE_RANGE_BREAK:
                    msg = f"RANGE BREAK at ${float(self.state.mid_price):,.2f}. Pausing replacements."
                    print_alert("warn", msg)
                    if self.cfg.telegram_alert_on_range_break:
                        self.alerter.send(
                            f"⚠️ <b>RANGE BREAK</b>\n"
                            f"Mid: ${float(self.state.mid_price):,.2f}\n"
                            f"Range: ${float(self.state.range_lower):,.2f} — "
                            f"${float(self.state.range_upper):,.2f}"
                        )
        else:
            if self._paused:
                self._paused = False
                self._pause_reason = None
                print_alert("ok", "Risk cleared. Resuming grid replacements.")

    # ─── RUN LOOP ────────────────────────────────────────────

    def run(self) -> None:
        if self.cfg.verbose_logging:
            with Live(
                build_dashboard(self.state, self.cfg),
                console=console,
                refresh_per_second=2,
                screen=False,
                transient=False,
            ) as live:
                while True:
                    try:
                        self.tick()
                        live.update(build_dashboard(self.state, self.cfg))
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print_alert("warn", f"tick error: {e}")
                    time.sleep(self.cfg.refresh_interval_seconds)
        else:
            while True:
                try:
                    self.tick()
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print_alert("warn", f"tick error: {e}")
                time.sleep(self.cfg.refresh_interval_seconds)

    # ─── SHUTDOWN ────────────────────────────────────────────

    def shutdown(self) -> None:
        print_info("Shutdown signal received. Cancelling all open grid orders…")
        cancelled = 0
        # Pull fresh open orders to ensure we cancel everything we created
        for o in self.client.get_open_orders():
            # Cancel any order that we have in state OR any open order on this asset
            # (better to be aggressive than leave dangling orders)
            ours = any(
                state_order.exchange_oid == o.oid
                for state_order in self.state.grid_orders.values()
            )
            if ours:
                if self.client.cancel_order(o.oid):
                    cancelled += 1
                time.sleep(0.08)

        print_alert("ok", f"Cancelled {cancelled} grid orders. Goodbye.")

        if self.alerter.enabled:
            self.alerter.send(
                f"🛑 <b>Bot stopped</b>\n"
                f"Fills: {self.state.total_fills}\n"
                f"Volume: ${float(self.state.total_volume_usd):,.2f}\n"
                f"Realized P&L: ${float(self.state.realized_pnl):,.2f}\n"
                f"Maker Rebates: ${float(self.state.maker_rebates_total):,.2f}"
            )
