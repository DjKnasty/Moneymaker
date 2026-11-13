#!/usr/bin/env python3
"""Solana whale-wallet watcher.

Read-only: never signs, never touches a wallet, never trades.
Polls 7 tracked wallets about every 60 seconds via Helius
getSignaturesForAddress, parses only new signatures, and POSTs
source=whale alerts to the same Wealth Creation webhook used by
memescan-lite. The webhook routine is the only thing that may trade.

HELIUS_API_KEY is read from the process environment at runtime.
It is never written to a file or to the log.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import signal
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
LITE_DIR = BASE.parent / "lite"
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc

WALLETS_PATH = BASE / "wallets.json"
STATE_PATH = BASE / "state.json"
LOG_PATH = BASE / "watch.log"
ALERTS_PATH = BASE / "alerts.jsonl"
PID_FILE = BASE / "watch_whales.pid"
POSITION_FLAG = LITE_DIR / "POSITION_OPEN"
ENV_PATHS = (LITE_DIR / ".env", BASE / ".env")

POLL_SECONDS = 60
SIGS_LIMIT = 25
MIN_BUY_SOL = 1.0
MAX_MCAP = 5_000_000.0
MIN_LIQ = 50_000.0
MIN_LIQ_MCAP = 0.03
MAX_CHANGE_1H = 30.0
MAX_CHANGE_24H = 150.0
DEDUPE_HOURS = 6
CLUSTER_HOURS = 2
PARSE_BATCH = 20
BACKOFF_MAX = 120

HELIUS_RPC = "https://mainnet.helius-rpc.com/"
HELIUS_API = "https://api.helius.xyz"
DEX_TOKENS = "https://api.dexscreener.com/latest/dex/tokens/"
RUGCHECK = "https://api.rugcheck.xyz/v1/tokens/{mint}/report"
SOL_MINT = "So11111111111111111111111111111111111111112"
UA = {"User-Agent": "memescan-whales/1.0", "accept": "application/json"}
NULL_KEYS = (None, "", "11111111111111111111111111111111")

MAJORS = {
    SOL_MINT,
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    "2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo",  # PYUSD
    "USDSwr9ApdHk5bvJKMjzFf41GhXeK9B4B2bStSj9co",
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",  # JUP
    "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4",  # JLP
    "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",  # JITO
    "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",  # jitoSOL
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",  # mSOL
    "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1",  # bSOL
    "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm",  # INF
    "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",  # WBTC
    "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",  # WETH
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
    "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",  # WIF
}

_stop = False
_req_count = 0
_rl_hits = 0
_sol_price = 0.0
_sol_price_ts = 0.0


def redact(text) -> str:
    s = str(text)
    key = os.environ.get("HELIUS_API_KEY") or ""
    hook = os.environ.get("WEALTH_WEBHOOK_KEY") or ""
    if key:
        s = s.replace(key, "[REDACTED]")
    if hook:
        s = s.replace(hook, "[REDACTED]")
    return s


def now_et() -> dt.datetime:
    return dt.datetime.now(ET)


def iso_et(t=None) -> str:
    return (t or now_et()).isoformat(timespec="seconds")


def fnum(v, default=0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def log_line(msg: str) -> None:
    line = redact(msg).rstrip() + "\n"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(line)
    if sys.stdout.isatty() or os.environ.get("WHALE_LOG_STDOUT") == "1":
        print(line, end="", flush=True)


def append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def load_dotenv() -> None:
    for path in ENV_PATHS:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip("'").strip('"')
            if k == "HELIUS_API_KEY":
                # Never load the Helius key from a file.
                continue
            if k and k not in os.environ:
                os.environ[k] = v


def helius_key() -> str:
    key = os.environ.get("HELIUS_API_KEY") or ""
    if not key:
        raise RuntimeError("HELIUS_API_KEY is not set in the environment")
    return key


def _http_json(url, data=None, headers=None, method=None, tries=3, timeout=30, sleep=0.8):
    global _req_count, _rl_hits
    last = None
    hdrs = dict(UA)
    if headers:
        hdrs.update(headers)
    body = data if data is None or isinstance(data, (bytes, bytearray)) else data
    for i in range(tries):
        try:
            _req_count += 1
            req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as f:
                raw = f.read()
                if not raw:
                    return None
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            raw = e.read()[:400] if e.fp else b""
            last = RuntimeError(redact(f"HTTP {e.code} {raw.decode('utf-8', 'replace')}"))
            if e.code == 429:
                _rl_hits += 1
                time.sleep(min(BACKOFF_MAX, 2.5 * (i + 1) ** 2))
            elif i < tries - 1:
                time.sleep(sleep * (i + 1))
        except Exception as e:
            last = RuntimeError(redact(e))
            if i < tries - 1:
                time.sleep(sleep * (i + 1))
    raise last


def helius_rpc(method, params, tries=3, timeout=30):
    url = HELIUS_RPC + "?api-key=" + helius_key()
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    data = _http_json(
        url,
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
        tries=tries,
        timeout=timeout,
    )
    if data and data.get("error"):
        raise RuntimeError(redact(data["error"]))
    return (data or {}).get("result")


def helius_parse(signatures, tries=3, timeout=40):
    if not signatures:
        return []
    url = HELIUS_API + "/v0/transactions?api-key=" + helius_key()
    body = json.dumps({"transactions": signatures}).encode()
    data = _http_json(
        url,
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
        tries=tries,
        timeout=timeout,
    )
    return data or []


def helius_txs_for_address(address, gte, lte, limit=100, pagination_token=None):
    opts = {
        "transactionDetails": "signatures",
        "filters": {"blockTime": {"gte": int(gte), "lte": int(lte)}},
        "limit": int(limit),
    }
    if pagination_token:
        opts["paginationToken"] = pagination_token
    return helius_rpc("getTransactionsForAddress", [address, opts]) or {}


def load_wallets():
    raw = json.loads(WALLETS_PATH.read_text())
    wallets = raw.get("wallets") or raw
    out = []
    for w in wallets:
        addr = (w.get("address") or "").strip()
        if not addr:
            continue
        out.append({
            "address": addr,
            "id": w.get("id") or w.get("name") or addr[:8],
            "name": w.get("name") or w.get("id") or addr[:8],
            "typical_buy_sol": w.get("typical_buy_sol"),
            "source": w.get("source"),
        })
    return out


def wallet_by_addr(wallets):
    return {w["address"]: w for w in wallets}


def default_state(wallets):
    return {
        "cursors": {w["address"]: {"sig": None, "ts": None} for w in wallets},
        "alerted": {},
        "recent_buys": [],
        "req_count": 0,
        "rl_hits": 0,
    }


def load_state(wallets):
    state = default_state(wallets)
    if STATE_PATH.exists():
        try:
            prev = json.loads(STATE_PATH.read_text())
            state["cursors"].update(prev.get("cursors") or {})
            state["alerted"] = prev.get("alerted") or {}
            state["recent_buys"] = prev.get("recent_buys") or []
            state["req_count"] = int(prev.get("req_count") or 0)
            state["rl_hits"] = int(prev.get("rl_hits") or 0)
        except Exception as e:
            log_line(f"{iso_et()} state load failed, starting fresh: {e}")
    # drop cursors for wallets no longer tracked
    addrs = {w["address"] for w in wallets}
    state["cursors"] = {k: v for k, v in state["cursors"].items() if k in addrs}
    for w in wallets:
        state["cursors"].setdefault(w["address"], {"sig": None, "ts": None})
    return state


def save_state(state):
    state = dict(state)
    state["req_count"] = _req_count
    state["rl_hits"] = _rl_hits
    state["saved"] = iso_et()
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(STATE_PATH)


def prune_state(state):
    cutoff_alert = now_et() - dt.timedelta(hours=DEDUPE_HOURS)
    cleaned = {}
    for mint, rec in (state.get("alerted") or {}).items():
        ts = rec.get("ts") if isinstance(rec, dict) else rec
        try:
            t = dt.datetime.fromisoformat(str(ts))
            if t.tzinfo is None:
                t = t.replace(tzinfo=ET)
            if t >= cutoff_alert:
                cleaned[mint] = rec if isinstance(rec, dict) else {"ts": ts, "wallets": []}
        except Exception:
            continue
    state["alerted"] = cleaned
    cutoff_buy = now_et() - dt.timedelta(hours=CLUSTER_HOURS)
    kept = []
    for b in state.get("recent_buys") or []:
        try:
            t = dt.datetime.fromisoformat(str(b.get("ts")))
            if t.tzinfo is None:
                t = t.replace(tzinfo=ET)
            if t >= cutoff_buy:
                kept.append(b)
        except Exception:
            continue
    state["recent_buys"] = kept
    return state


def position_open() -> bool:
    return POSITION_FLAG.exists()


def get_signatures(address, until_sig=None, limit=SIGS_LIMIT):
    opts = {"limit": int(limit)}
    if until_sig:
        # 'until' is exclusive: stop at the already-seen cursor
        opts["until"] = until_sig
    return helius_rpc("getSignaturesForAddress", [address, opts]) or []


def token_deltas(tx, wallet):
    """Return {mint: ui_amount_delta} for the wallet from accountData and transfers."""
    deltas = {}
    for a in tx.get("accountData") or []:
        for c in a.get("tokenBalanceChanges") or []:
            if c.get("userAccount") != wallet:
                continue
            mint = c.get("mint")
            raw = c.get("rawTokenAmount") or {}
            amt = fnum(raw.get("tokenAmount"))
            dec = int(fnum(raw.get("decimals")))
            ui = amt / (10 ** dec) if dec else amt
            deltas[mint] = deltas.get(mint, 0.0) + ui
    for t in tx.get("tokenTransfers") or []:
        mint = t.get("mint")
        amt = fnum(t.get("tokenAmount"))
        if t.get("toUserAccount") == wallet:
            deltas[mint] = deltas.get(mint, 0.0) + amt
        if t.get("fromUserAccount") == wallet:
            deltas[mint] = deltas.get(mint, 0.0) - amt
    return deltas


def native_change(tx, wallet) -> int:
    for a in tx.get("accountData") or []:
        if a.get("account") == wallet:
            return int(a.get("nativeBalanceChange") or 0)
    native_out = 0
    native_in = 0
    for n in tx.get("nativeTransfers") or []:
        amt = int(n.get("amount") or 0)
        if n.get("fromUserAccount") == wallet:
            native_out += amt
        if n.get("toUserAccount") == wallet:
            native_in += amt
    return native_in - native_out


def involved(tx, wallet) -> bool:
    if tx.get("feePayer") == wallet:
        return True
    if native_change(tx, wallet):
        return True
    if token_deltas(tx, wallet):
        return True
    return False


def extract_buy(tx, wallet, sol_price: float):
    """Return a buy dict if the wallet bought a non-major SPL token with SOL/USDC."""
    if tx.get("transactionError"):
        return None
    if not involved(tx, wallet):
        return None
    typ = (tx.get("type") or "").upper()
    if typ and typ not in ("SWAP", "BUY", "UNKNOWN", ""):
        # Still allow SWAP-like txs with token deltas even if typed TRANSFER
        deltas = token_deltas(tx, wallet)
        received = [m for m, a in deltas.items() if a > 0 and m and m not in MAJORS]
        if typ == "TRANSFER" and not received:
            return None
        if typ not in ("SWAP", "BUY", "TRANSFER"):
            if not received:
                return None
    deltas = token_deltas(tx, wallet)
    received = [(m, a) for m, a in deltas.items() if a > 0 and m and m not in MAJORS]
    sent_majors = [(m, -a) for m, a in deltas.items() if a < 0 and m in MAJORS]
    if not received:
        return None
    # Prefer the largest received meme mint
    received.sort(key=lambda x: -abs(x[1]))
    mint, token_amount = received[0]
    nb = native_change(tx, wallet)
    sol_spent = max(0.0, -nb) / 1e9 if nb < 0 else 0.0
    stable_spent = sum(a for _, a in sent_majors)
    sol_equiv = sol_spent
    if stable_spent and sol_price > 0:
        sol_equiv += stable_spent / sol_price
    elif stable_spent:
        sol_equiv += stable_spent / 100.0  # conservative fallback
    if sol_equiv < MIN_BUY_SOL and sol_spent < MIN_BUY_SOL and stable_spent < (sol_price or 100.0) * MIN_BUY_SOL:
        return None
    return {
        "mint": mint,
        "token_amount": token_amount,
        "sol_spent": round(sol_spent, 6),
        "stable_spent": round(stable_spent, 4),
        "sol_equiv": round(sol_equiv, 6),
        "source": tx.get("source"),
        "type": tx.get("type"),
        "signature": tx.get("signature"),
        "timestamp": tx.get("timestamp"),
        "fee_payer": tx.get("feePayer"),
        "price_paid_sol": (sol_equiv / token_amount) if token_amount else None,
    }


def refresh_sol_price(force=False) -> float:
    global _sol_price, _sol_price_ts
    if not force and _sol_price and time.time() - _sol_price_ts < 300:
        return _sol_price
    try:
        d = _http_json(DEX_TOKENS + SOL_MINT, tries=2, timeout=15)
        pairs = (d or {}).get("pairs") or (d if isinstance(d, list) else [])
        best = 0.0
        for p in pairs or []:
            if (p.get("chainId") or "").lower() != "solana":
                continue
            best = max(best, fnum(p.get("priceUsd")))
        if best:
            _sol_price = best
            _sol_price_ts = time.time()
    except Exception as e:
        log_line(f"{iso_et()} sol price fetch failed: {e}")
    return _sol_price


def enrich_dex(mints):
    out = {}
    uniq = [m for m in dict.fromkeys(mints) if m]
    for i in range(0, len(uniq), 30):
        chunk = uniq[i : i + 30]
        try:
            d = _http_json(DEX_TOKENS + ",".join(chunk), tries=2, timeout=20)
        except Exception as e:
            log_line(f"{iso_et()} dexscreener fail: {e}")
            continue
        pairs = (d or {}).get("pairs") or (d if isinstance(d, list) else [])
        best = {}
        for p in pairs or []:
            if (p.get("chainId") or "").lower() != "solana":
                continue
            mint = (p.get("baseToken") or {}).get("address")
            if not mint or mint in MAJORS:
                continue
            liq = fnum((p.get("liquidity") or {}).get("usd"))
            vol = fnum((p.get("volume") or {}).get("h24"))
            cur = best.get(mint)
            if cur is None or (liq, vol) > (cur[0], cur[1]):
                best[mint] = (liq, vol, p)
        for mint, (_, _, p) in best.items():
            base = p.get("baseToken") or {}
            created = p.get("pairCreatedAt")
            age_h = None
            if created:
                try:
                    age_h = (time.time() - float(created) / 1000.0) / 3600.0
                except Exception:
                    age_h = None
            ch = p.get("priceChange") or {}
            rec = {
                "symbol": base.get("symbol") or "?",
                "name": base.get("name") or base.get("symbol") or "?",
                "price": fnum(p.get("priceUsd")),
                "mcap": fnum(p.get("marketCap") or p.get("fdv")),
                "fdv": fnum(p.get("fdv")),
                "liq": fnum((p.get("liquidity") or {}).get("usd")),
                "vol24": fnum((p.get("volume") or {}).get("h24")),
                "change_1h": fnum(ch.get("h1")),
                "change_24h": fnum(ch.get("h24")),
                "pair": p.get("pairAddress"),
                "dex": p.get("dexId"),
                "pool_age_hours": round(age_h, 3) if age_h is not None else None,
            }
            rec["liq_over_mcap"] = (rec["liq"] / rec["mcap"]) if rec["mcap"] else None
            out[mint] = rec
        time.sleep(0.15)
    return out


def rugcheck_pre(mint):
    try:
        d = _http_json(RUGCHECK.format(mint=mint), tries=2, timeout=20)
    except Exception as e:
        return {"ok": None, "error": redact(e), "mint_revoked": None, "freeze_revoked": None}
    mint_auth = (d or {}).get("mintAuthority")
    freeze_auth = (d or {}).get("freezeAuthority")
    return {
        "ok": True,
        "mint_authority": mint_auth,
        "freeze_authority": freeze_auth,
        "mint_revoked": mint_auth in NULL_KEYS,
        "freeze_revoked": freeze_auth in NULL_KEYS,
        "rugged": (d or {}).get("rugged"),
        "score_norm": (d or {}).get("score_normalised"),
    }


def good_price(enr):
    reasons = []
    if not enr:
        return False, ["dex_unknown"]
    mcap = fnum(enr.get("mcap"))
    liq = fnum(enr.get("liq"))
    c1 = enr.get("change_1h")
    c24 = enr.get("change_24h")
    ratio = enr.get("liq_over_mcap")
    if mcap <= 0:
        reasons.append("mcap_unknown")
    elif mcap > MAX_MCAP:
        reasons.append(f"mcap>{MAX_MCAP:.0f}")
    if liq < MIN_LIQ:
        reasons.append(f"liq<{MIN_LIQ:.0f}")
    if ratio is None:
        reasons.append("liq_mcap_unknown")
    elif ratio < MIN_LIQ_MCAP:
        reasons.append(f"liq/mcap<{MIN_LIQ_MCAP}")
    if c1 is not None and c1 > MAX_CHANGE_1H:
        reasons.append(f"chg1h>{MAX_CHANGE_1H}")
    if c24 is not None and c24 > MAX_CHANGE_24H:
        reasons.append(f"chg24h>{MAX_CHANGE_24H}")
    return (not reasons), reasons


def cluster_wallets(state, mint, wallet, ts_iso):
    addrs = {wallet}
    try:
        t0 = dt.datetime.fromisoformat(ts_iso)
        if t0.tzinfo is None:
            t0 = t0.replace(tzinfo=ET)
    except Exception:
        t0 = now_et()
    for b in state.get("recent_buys") or []:
        if b.get("mint") != mint:
            continue
        try:
            t = dt.datetime.fromisoformat(str(b.get("ts")))
            if t.tzinfo is None:
                t = t.replace(tzinfo=ET)
        except Exception:
            continue
        if abs((t0 - t).total_seconds()) <= CLUSTER_HOURS * 3600:
            addrs.add(b.get("wallet"))
    addrs.discard(None)
    return sorted(addrs)


def should_alert(state, mint, wallet, ts_iso):
    rec = (state.get("alerted") or {}).get(mint)
    if not rec:
        return True, "new"
    try:
        t = dt.datetime.fromisoformat(str(rec.get("ts")))
        if t.tzinfo is None:
            t = t.replace(tzinfo=ET)
        if now_et() - t > dt.timedelta(hours=DEDUPE_HOURS):
            return True, "expired"
    except Exception:
        return True, "bad_state"
    prev = set(rec.get("wallets") or [])
    if wallet not in prev:
        return True, "new_wallet"
    return False, "deduped"


def payload_coin(mint, enr, wallets_info, checks, ts, priority, extras):
    first = wallets_info[0] if wallets_info else {}
    body = {
        "mint": mint,
        "symbol": (enr or {}).get("symbol") or "?",
        "price": (enr or {}).get("price") or 0,
        "mcap": (enr or {}).get("mcap") or 0,
        "liq": (enr or {}).get("liq") or 0,
        "vol": (enr or {}).get("vol24") or 0,
        "lane": None,
        "socials": {},
        "social_score": 0,
        "checks": checks or {},
        "timestamp": ts,
        "source": "whale",
        "wallets": wallets_info,
        "wallet": first.get("address"),
        "buy_size_sol": first.get("buy_sol"),
        "tx_signature": first.get("signature"),
        "price_paid": first.get("price_paid"),
        "priority": priority,
        "change_1h": (enr or {}).get("change_1h"),
        "change_24h": (enr or {}).get("change_24h"),
        "pool_age_hours": (enr or {}).get("pool_age_hours"),
        "liq_over_mcap": (enr or {}).get("liq_over_mcap"),
    }
    if extras:
        body.update(extras)
    return body


def post_webhook(passers, ts, disabled=False):
    if not passers:
        return "skip_empty"
    if disabled:
        return "disabled"
    url = os.environ.get("WEALTH_WEBHOOK_URL") or ""
    key = os.environ.get("WEALTH_WEBHOOK_KEY") or ""
    if not url or not key:
        log_line(f"{ts} webhook skipped: WEALTH_WEBHOOK_URL or WEALTH_WEBHOOK_KEY missing")
        return "missing_env"
    body = json.dumps({"timestamp": ts, "passers": passers}).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "x-webhook-key": key,
    }
    try:
        _http_json(url, data=body, headers=headers, method="POST", tries=2, timeout=20)
        return "posted"
    except Exception as e:
        log_line(f"{ts} webhook POST failed: {e}")
        return f"error:{e}"[:160]


def new_signatures(address, cursor_sig):
    """Return new signatures newest-first, stopping at the cursor. Updates nothing."""
    try:
        sigs = get_signatures(address, until_sig=cursor_sig, limit=SIGS_LIMIT)
    except Exception:
        # some nodes reject `until` if the cursor is too old; retry without it
        sigs = get_signatures(address, until_sig=None, limit=SIGS_LIMIT)
    out = []
    for s in sigs:
        sig = s.get("signature")
        if not sig:
            continue
        if cursor_sig and sig == cursor_sig:
            break
        out.append(s)
    return out


def parse_new(sigs):
    parsed = []
    uniq = []
    seen = set()
    for s in sigs:
        sig = s.get("signature") if isinstance(s, dict) else s
        if not sig or sig in seen:
            continue
        seen.add(sig)
        uniq.append(sig)
    for i in range(0, len(uniq), PARSE_BATCH):
        chunk = uniq[i : i + PARSE_BATCH]
        try:
            parsed.extend(helius_parse(chunk))
        except Exception as e:
            log_line(f"{iso_et()} parse failed ({len(chunk)} sigs): {e}")
        if i + PARSE_BATCH < len(uniq):
            time.sleep(0.15)
    by_sig = {t.get("signature"): t for t in parsed if t.get("signature")}
    return by_sig


def process_buys(buys, wallets, state, ts, post, backfill=False):
    """buys: list of dicts with wallet, buy, wallet_meta."""
    if not buys:
        return {"detected": 0, "passed": 0, "posted": 0, "logged": 0}
    index = wallet_by_addr(wallets)
    mints = [b["buy"]["mint"] for b in buys]
    enriched = enrich_dex(mints)
    pos = position_open()
    posted = 0
    passed = 0
    payloads = []
    for item in buys:
        wallet = item["wallet"]
        buy = item["buy"]
        meta = index.get(wallet) or {"address": wallet, "id": wallet[:8], "name": wallet[:8]}
        mint = buy["mint"]
        enr = enriched.get(mint)
        ok, reasons = good_price(enr)
        cluster = cluster_wallets(state, mint, wallet, ts)
        if wallet not in cluster:
            cluster.append(wallet)
        multi = len(set(cluster)) >= 2
        record = {
            "ts": ts,
            "event": "buy",
            "backfill": backfill,
            "would_have_alerted": False,
            "wallet": wallet,
            "wallet_id": meta.get("id"),
            "wallet_name": meta.get("name"),
            "mint": mint,
            "symbol": (enr or {}).get("symbol"),
            "buy": buy,
            "enrichment": enr,
            "good_price": ok,
            "filter_reasons": reasons,
            "cluster_wallets": cluster,
            "priority": "multi" if multi else "normal",
            "position_open": pos,
        }
        state.setdefault("recent_buys", []).append({
            "mint": mint,
            "wallet": wallet,
            "ts": ts,
            "signature": buy.get("signature"),
            "sol_equiv": buy.get("sol_equiv"),
        })
        if not ok:
            record["event"] = "filtered"
            append_jsonl(ALERTS_PATH, record)
            continue
        # rugcheck only after the cheap filter
        rc = rugcheck_pre(mint)
        checks = {
            "mint_authority_revoked": rc.get("mint_revoked"),
            "freeze_authority_revoked": rc.get("freeze_revoked"),
            "rugged": rc.get("rugged"),
            "rugcheck_ok": rc.get("ok"),
        }
        if rc.get("error"):
            checks["rugcheck_error"] = str(rc.get("error"))[:160]
        record["checks"] = checks
        alert, why = should_alert(state, mint, wallet, ts)
        record["dedupe"] = why
        if not alert:
            record["event"] = "deduped"
            append_jsonl(ALERTS_PATH, record)
            continue
        wallets_info = [{
            "address": wallet,
            "id": meta.get("id"),
            "name": meta.get("name"),
            "buy_sol": buy.get("sol_equiv") or buy.get("sol_spent"),
            "price_paid": buy.get("price_paid_sol"),
            "signature": buy.get("signature"),
            "tx_time": buy.get("timestamp"),
            "tx_source": buy.get("source"),
        }]
        # attach other cluster wallets if we have them in recent_buys
        seen_w = {wallet}
        for b in state.get("recent_buys") or []:
            if b.get("mint") == mint and b.get("wallet") not in seen_w:
                seen_w.add(b["wallet"])
                other = index.get(b["wallet"]) or {}
                wallets_info.append({
                    "address": b["wallet"],
                    "id": other.get("id"),
                    "name": other.get("name"),
                    "buy_sol": b.get("sol_equiv"),
                    "signature": b.get("signature"),
                })
        extras = {"would_have_alerted": backfill, "backfill": backfill} if backfill else {}
        payload = payload_coin(
            mint, enr, wallets_info, checks, ts,
            "multi" if multi else "normal", extras,
        )
        record["event"] = "would_have_alerted" if (backfill or pos or not post) else "alert"
        record["would_have_alerted"] = True
        record["payload"] = payload
        append_jsonl(ALERTS_PATH, record)
        passed += 1
        if backfill or pos or not post:
            # Mark dedupe on the in-memory state so repeat fills in one run
            # collapse to one would-have-alerted. Backfill uses a throwaway state
            # and never writes cursors or live alerted.json.
            rec = state.setdefault("alerted", {}).get(mint) or {"ts": ts, "wallets": []}
            rec["ts"] = ts
            rec.setdefault("wallets", [])
            if wallet not in rec["wallets"]:
                rec["wallets"].append(wallet)
            state["alerted"][mint] = rec
            continue
        payloads.append(payload)
        rec = state.setdefault("alerted", {}).get(mint) or {"ts": ts, "wallets": []}
        rec["ts"] = ts
        rec.setdefault("wallets", [])
        if wallet not in rec["wallets"]:
            rec["wallets"].append(wallet)
        state["alerted"][mint] = rec

    status = "skip"
    if payloads:
        status = post_webhook(payloads, ts, disabled=not post)
        if status == "posted":
            posted = len(payloads)
        log_line(f"{ts} webhook={status} n={len(payloads)}")
    return {"detected": len(buys), "passed": passed, "posted": posted, "logged": len(buys), "webhook": status}


def collect_wallet_buys(address, sig_rows, parsed, sol_price):
    buys = []
    skipped = 0
    for s in sig_rows:
        sig = s.get("signature")
        tx = parsed.get(sig)
        if not tx:
            continue
        if s.get("err") or tx.get("transactionError"):
            continue
        buy = extract_buy(tx, address, sol_price)
        if buy:
            # fill timestamp from signature if missing
            if not buy.get("timestamp"):
                buy["timestamp"] = s.get("blockTime")
            buys.append(buy)
        else:
            skipped += 1
    return buys, skipped


def advance_cursor(state, address, sig_rows):
    if not sig_rows:
        return
    newest = sig_rows[0]
    state["cursors"][address] = {
        "sig": newest.get("signature"),
        "ts": newest.get("blockTime"),
    }


def seed_cursors(wallets, state):
    """On first run, record the latest signature so we do not alert historical buys."""
    seeded = 0
    for w in wallets:
        cur = state["cursors"].get(w["address"]) or {}
        if cur.get("sig"):
            continue
        try:
            sigs = get_signatures(w["address"], limit=1)
            time.sleep(0.12)
        except Exception as e:
            log_line(f"{iso_et()} seed cursor fail {w['id']}: {e}")
            continue
        if sigs:
            state["cursors"][w["address"]] = {
                "sig": sigs[0].get("signature"),
                "ts": sigs[0].get("blockTime"),
            }
            seeded += 1
    if seeded:
        save_state(state)
        log_line(f"{iso_et()} seeded {seeded} wallet cursors (no historical alerts)")
    return seeded


def run_cycle(wallets, state, post=True):
    ts = iso_et()
    state = prune_state(state)
    sol_price = refresh_sol_price()
    detected = []
    new_sig_n = 0
    parse_n = 0
    errors = 0
    for i, w in enumerate(wallets):
        addr = w["address"]
        cursor = (state["cursors"].get(addr) or {}).get("sig")
        try:
            rows = new_signatures(addr, cursor)
        except Exception as e:
            errors += 1
            log_line(f"{ts} sigs fail {w['id']}: {e}")
            time.sleep(0.15)
            continue
        if rows:
            new_sig_n += len(rows)
            parsed = parse_new(rows)
            parse_n += len(parsed)
            buys, _ = collect_wallet_buys(addr, rows, parsed, sol_price)
            for b in buys:
                detected.append({"wallet": addr, "buy": b})
            advance_cursor(state, addr, rows)
        if i < len(wallets) - 1:
            time.sleep(0.12)
    stats = process_buys(detected, wallets, state, ts, post=post, backfill=False)
    save_state(state)
    log_line(
        f"{ts} cycle wallets={len(wallets)} new_sigs={new_sig_n} parsed={parse_n} "
        f"buys={stats['detected']} passed={stats['passed']} posted={stats['posted']} "
        f"position_open={int(position_open())} errors={errors} "
        f"reqs={_req_count} rl_hits={_rl_hits} sol=${sol_price:.2f}"
    )
    return stats


def backfill(wallets, hours=24, post=False):
    ts = iso_et()
    end = int(time.time())
    start = end - int(hours * 3600)
    sol_price = refresh_sol_price(force=True)
    log_line(f"{ts} backfill start hours={hours} post={int(post)} wallets={len(wallets)}")
    all_buys = []
    for w in wallets:
        addr = w["address"]
        token = None
        rows = []
        pages = 0
        while pages < 8:
            pages += 1
            try:
                res = helius_txs_for_address(addr, start, end, limit=100, pagination_token=token)
            except Exception as e:
                log_line(f"{ts} backfill sigs fail {w['id']}: {e}")
                break
            data = (res or {}).get("data") or []
            rows.extend(data)
            token = (res or {}).get("paginationToken")
            if not token or not data:
                break
            time.sleep(0.15)
        if not rows:
            log_line(f"{ts} backfill {w['id']}: 0 signatures in window")
            continue
        parsed = parse_new(rows)
        buys, _ = collect_wallet_buys(addr, rows, parsed, sol_price)
        log_line(f"{ts} backfill {w['id']}: sigs={len(rows)} parsed={len(parsed)} meme_buys>={MIN_BUY_SOL}SOL={len(buys)}")
        for b in buys:
            all_buys.append({"wallet": addr, "buy": b})
        time.sleep(0.2)
    # A throwaway state so backfill does not rewrite live cursors / live dedupe
    temp = default_state(wallets)
    stats = process_buys(all_buys, wallets, temp, ts, post=False, backfill=True)
    log_line(
        f"{ts} backfill done detected={stats['detected']} would_have_alerted={stats['passed']} "
        f"reqs={_req_count} rl_hits={_rl_hits}"
    )
    return stats


def handle_stop(signum, frame):
    global _stop
    _stop = True
    log_line(f"{iso_et()} received signal {signum}, stopping")


def write_pid():
    PID_FILE.write_text(str(os.getpid()))


def clear_pid():
    try:
        if PID_FILE.exists() and PID_FILE.read_text().strip() == str(os.getpid()):
            PID_FILE.unlink()
    except Exception:
        pass


def loop(post=True):
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)
    write_pid()
    load_dotenv()
    wallets = load_wallets()
    state = load_state(wallets)
    global _req_count, _rl_hits
    _req_count = int(state.get("req_count") or 0)
    _rl_hits = int(state.get("rl_hits") or 0)
    log_line(f"{iso_et()} loop started pid={os.getpid()} wallets={len(wallets)} poll={POLL_SECONDS}s post={int(post)}")
    try:
        seed_cursors(wallets, state)
        while not _stop:
            started = time.time()
            try:
                run_cycle(wallets, state, post=post)
            except Exception:
                log_line(f"{iso_et()} cycle error:\n{redact(traceback.format_exc())}")
                time.sleep(5)
            wait = POLL_SECONDS - (time.time() - started)
            end = time.time() + max(0.0, wait)
            while not _stop and time.time() < end:
                time.sleep(min(5.0, max(0.1, end - time.time())))
    finally:
        clear_pid()
        log_line(f"{iso_et()} loop stopped")


def main(argv=None):
    p = argparse.ArgumentParser(description="Solana whale-wallet watcher (alerts only, never trades)")
    p.add_argument("--loop", action="store_true", help="run the 60s poll loop")
    p.add_argument("--once", action="store_true", help="run a single poll cycle")
    p.add_argument("--backfill-hours", type=float, default=0, help="backfill this many hours without posting")
    p.add_argument("--no-post", action="store_true", help="do not POST to the webhook")
    args = p.parse_args(argv)
    load_dotenv()
    # fail fast if the key is missing
    helius_key()
    wallets = load_wallets()
    if not wallets:
        print("no wallets in wallets.json", file=sys.stderr)
        return 2
    post = not args.no_post
    if args.backfill_hours:
        backfill(wallets, hours=args.backfill_hours, post=False)
    if args.once:
        state = load_state(wallets)
        seed_cursors(wallets, state)
        run_cycle(wallets, state, post=post)
        return 0
    if args.loop or not args.backfill_hours:
        if not args.loop and not args.once and not args.backfill_hours:
            # default is the standing loop
            loop(post=post)
        elif args.loop:
            loop(post=post)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
