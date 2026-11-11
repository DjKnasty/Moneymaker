#!/usr/bin/env python3
"""Compute current risk state from risk_rules.json and trades.jsonl.

Read-only. Never places a trade, never touches a wallet.
If trades.jsonl is missing, reports the rules and "no trades yet".

Expected trades.jsonl: one JSON object per closed trade, fields:
  pnl or pnl_usd: signed USD P&L
  equity or equity_after or closed_equity: wallet equity after the close (optional)
  result or outcome or exit: stop | tp | win | loss | ...
  ts or timestamp or closed_at: ISO timestamp
"""
from __future__ import annotations

import json
import sys
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
ET = ZoneInfo("America/New_York")
RULES_PATH = BASE / "risk_rules.json"
TRADES_PATH = BASE / "trades.jsonl"
OUT_PATH = BASE / "risk_state.json"


def fnum(v, default=None):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def parse_ts(t):
    if t is None or t == "":
        return None
    if isinstance(t, (int, float)):
        # seconds or ms
        v = float(t)
        if v > 1e12:
            v = v / 1000.0
        return dt.datetime.fromtimestamp(v, ET)
    s = str(t).replace("Z", "+00:00")
    try:
        x = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    if x.tzinfo is None:
        x = x.replace(tzinfo=ET)
    return x.astimezone(ET)


def load_rules():
    if not RULES_PATH.exists():
        raise SystemExit(f"missing {RULES_PATH}")
    return json.loads(RULES_PATH.read_text())


def load_trades():
    if not TRADES_PATH.exists():
        return None
    rows = []
    for i, line in enumerate(TRADES_PATH.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception as e:
            print(f"skip trades.jsonl line {i}: {e}", file=sys.stderr)
    return rows


def trade_pnl(t):
    return fnum(t.get("pnl_usd") if t.get("pnl_usd") is not None else t.get("pnl"))


def trade_equity(t):
    for k in ("equity_after", "closed_equity", "equity", "wallet_equity"):
        v = fnum(t.get(k))
        if v is not None:
            return v
    return None


def trade_ts(t):
    for k in ("closed_at", "timestamp", "ts", "time", "exited_at"):
        x = parse_ts(t.get(k))
        if x is not None:
            return x
    return None


def is_stop(t):
    r = str(t.get("result") or t.get("outcome") or t.get("exit") or "").lower().strip()
    if r in ("stop", "stopped", "sl", "stop_loss", "stopped_out", "stop-loss"):
        return True
    return False


def is_win(t):
    r = str(t.get("result") or t.get("outcome") or t.get("exit") or "").lower().strip()
    if r in ("tp", "take_profit", "take-profit", "win", "profit"):
        return True
    pnl = trade_pnl(t)
    return (not is_stop(t)) and pnl is not None and pnl > 0


def compute(rules, trades):
    sizing = rules.get("sizing") or {}
    dd = rules.get("drawdown") or {}
    start = fnum(rules.get("starting_equity_usd"), 0.0) or 0.0
    risk_pct = fnum(sizing.get("risk_pct_of_closed_equity"), 0.10)
    max_risk = fnum(sizing.get("max_risk_usd"), 40.0)
    halve_pct = fnum(dd.get("halve_risk_below_hwm_pct"), 20.0)
    pause_pct = fnum(dd.get("pause_and_ask_below_hwm_pct"), 35.0)
    stop_n = int(dd.get("consecutive_stops_pause_day") or 3)
    day_loss_lim = fnum(dd.get("day_loss_pause_usd"), 40.0)

    now = dt.datetime.now(ET)
    today = now.date()

    out = {
        "timestamp": now.isoformat(timespec="seconds"),
        "timezone": "America/New_York",
        "trades_file": str(TRADES_PATH),
        "trades_found": False,
        "n_closed": 0,
        "starting_equity_usd": start,
        "closed_equity_usd": start,
        "hwm_usd": start,
        "drawdown_pct": 0.0,
        "consecutive_stops": 0,
        "day_pnl_usd": 0.0,
        "base_risk_usd": None,
        "allowed_risk_usd": 0.0,
        "entries_allowed": True,
        "pause_reason": None,
        "ask_thomas": False,
        "notes": [],
    }

    if trades is None:
        out["notes"].append("no trades yet (trades.jsonl missing)")
        base = min((risk_pct * start) if start else 0.0, max_risk)
        out["base_risk_usd"] = round(base, 2)
        out["allowed_risk_usd"] = round(base, 2)
        return out

    out["trades_found"] = True
    closed = []
    for t in trades:
        pnl = trade_pnl(t)
        eq = trade_equity(t)
        ts = trade_ts(t)
        # Skip obvious non-closes if a status field says open.
        st = str(t.get("status") or t.get("state") or "").lower()
        if st in ("open", "pending", "entry"):
            continue
        closed.append({"raw": t, "pnl": pnl, "equity": eq, "ts": ts, "stop": is_stop(t), "win": is_win(t)})
    out["n_closed"] = len(closed)

    equity = start
    hwm = start
    for c in closed:
        if c["pnl"] is not None and c["equity"] is None:
            equity = equity + c["pnl"]
        elif c["equity"] is not None:
            equity = c["equity"]
        if equity > hwm:
            hwm = equity
    if closed and all(c["equity"] is None for c in closed) and start == 0:
        out["notes"].append("trades have pnl but no equity and starting_equity_usd is 0; equity may be incomplete")

    out["closed_equity_usd"] = round(equity, 2)
    out["hwm_usd"] = round(hwm, 2)
    drawdown_pct = 0.0 if hwm <= 0 else max(0.0, (hwm - equity) / hwm * 100.0)
    out["drawdown_pct"] = round(drawdown_pct, 2)

    consec = 0
    for c in reversed(closed):
        if c["stop"]:
            consec += 1
            continue
        break
    out["consecutive_stops"] = consec

    day_pnl = 0.0
    for c in closed:
        if c["ts"] is not None and c["ts"].date() == today and c["pnl"] is not None:
            day_pnl += c["pnl"]
        elif c["ts"] is None and c["pnl"] is not None:
            out["notes"].append("a trade has pnl but no timestamp; omitted from day pnl")
    out["day_pnl_usd"] = round(day_pnl, 2)

    base = min(risk_pct * equity, max_risk) if equity > 0 else 0.0
    out["base_risk_usd"] = round(base, 2)
    allowed = base
    pause = None
    ask = False
    if drawdown_pct >= pause_pct:
        allowed = 0.0
        pause = f"{drawdown_pct:.1f}% below HWM (>= {pause_pct:.0f}%): pause new entries and ask Thomas"
        ask = True
    elif consec >= stop_n:
        allowed = 0.0
        pause = f"{consec} straight stops: stop entering for the rest of the day (America/New_York)"
    elif day_pnl <= -abs(day_loss_lim):
        allowed = 0.0
        pause = f"day PnL {day_pnl:.2f} reached -${day_loss_lim:.0f}: stop entering for the rest of the day (America/New_York)"
    elif drawdown_pct >= halve_pct:
        allowed = base / 2.0
        out["notes"].append(f"{drawdown_pct:.1f}% below HWM (>= {halve_pct:.0f}%): risk halved")

    out["allowed_risk_usd"] = round(allowed, 2)
    out["entries_allowed"] = allowed > 0
    out["pause_reason"] = pause
    out["ask_thomas"] = ask
    return out


def main():
    rules = load_rules()
    trades = load_trades()
    state = compute(rules, trades)
    OUT_PATH.write_text(json.dumps(state, indent=2, default=str) + "\n")
    print(json.dumps(state, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
