#!/usr/bin/env python3
"""Lightweight Solana meme-coin scanner.

Read-only. Never signs a transaction, never touches a wallet, never trades.
No LLM calls. Standard library only.

Two cheap-filter lanes (screener data first: GeckoTerminal + DexScreener,
plus a new-pools feed for Lane 2):
  Lane 1 (aged): >=12 hourly candles, 24h vol >= $250K, vol/mcap >= 0.4,
    liquidity $50K-$2.0M.
  Lane 2 (fresh): pool age 15 min to 12 h, >=1 hourly candle, 24h vol >= $100K,
    vol/mcap >= 0.5, liquidity >= $50K.
  Market cap is info-only (no lower or upper bound).
  The old 7-20x vol/liq gate is removed.
  Adjusted top-10 holders is shadow-logged only (not a gate).
  Social gate (after liq/vol, before candles/anti-rug): at least one
    X/Twitter or Telegram link. Website is a bonus. social_score is 0-3
    (X, Telegram, website). Generic/status X URLs and X links reused
    across mints in the same scan are flagged, not gated. If social
    APIs error, the coin is logged as social_unknown and fails closed.

Both lanes then go through the same anti-rug + hidden-fee stack,
including a RugCheck (api.rugcheck.xyz) token report:
  - mint and freeze authority revoked
  - LP locked or burned (>= 90% on the primary pool)
  - no honeypot
  - trading not paused
  - tax under 5% (pool-reported and on-chain Token-2022)
  - no proxy / live fee authority
  - no RugCheck danger-level risks or rugged=true
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc

GT = "https://api.geckoterminal.com/api/v2/networks/solana"
DEX_TOKENS = "https://api.dexscreener.com/latest/dex/tokens/"
DEX_TOKENS_V1 = "https://api.dexscreener.com/tokens/v1/solana/"
DEX_PROFILES = "https://api.dexscreener.com/token-profiles/latest/v1"
PUMP_COINS = (
    "https://frontend-api-v3.pump.fun/coins/{mint}",
    "https://frontend-api.pump.fun/coins/{mint}",
)
RUGCHECK = "https://api.rugcheck.xyz/v1/tokens/{mint}/report"
RPC = "https://api.mainnet-beta.solana.com"
UA = {"User-Agent": "memescan-lite/1.1", "accept": "application/json"}

# Market cap is info-only (gate removed 2026-11-11).
# Two-lane filters (approved 2026-11-11). Vol/liq 7-20x gate dropped.
LIQ_LO = 50_000
LIQ_HI_L1 = 2_000_000
VOL_L1 = 250_000
VOL_L2 = 100_000
TURN_L1 = 0.4
TURN_L2 = 0.5
MIN_CANDLES_L1 = 12
MIN_CANDLES_L2 = 1
AGE_L2_MIN_S = 15 * 60
AGE_L2_MAX_S = 12 * 3600
COLLECT_EARLY_VOL = 80_000  # early-exit floor on volume pages (0.8 * Lane 2 vol)
LP_MIN_PCT = 90.0
TAX_FAIL_PCT = 5.0
ADJ10_MAX = 30.0  # shadow-log only; not a gate
DEDUPE_HOURS = 6
POSITION_FLAG = BASE / "POSITION_OPEN"
ALERT_STATE = BASE / "alerted.json"
LOG_PATH = BASE / "scan.log"
LAST_PATH = BASE / "last_result.json"
SHADOW_PATH = BASE / "shadow_log.jsonl"
ENV_PATH = BASE / ".env"

# Per-run social lookup cache. Cleared at the start of each run().
SOCIAL_CACHE = {}
_PUMP_DISABLED = False

TWITTER_HOSTS = {
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
    "mobile.twitter.com",
    "mobile.x.com",
    "t.co",
}
TELEGRAM_HOSTS = {
    "t.me",
    "www.t.me",
    "telegram.me",
    "www.telegram.me",
    "telegram.org",
    "www.telegram.org",
    "telegram.dog",
}
# First path segment of an X/Twitter URL that is not a profile or community.
TWITTER_GENERIC_HEADS = {
    "",
    "home",
    "explore",
    "search",
    "login",
    "signup",
    "i",
    "intent",
    "share",
    "hashtag",
    "tos",
    "privacy",
    "settings",
    "notifications",
    "messages",
    "compose",
    "jobs",
    "about",
    "download",
    "security",
    "help",
    "terms",
    "account",
    "official",
    "web",
    "share",
}

NULL_KEYS = (None, "", "11111111111111111111111111111111")

# Known non-meme bases we never want as the scanned token.
SKIP_MINTS = {
    "So11111111111111111111111111111111111111112",  # WSOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB",
    "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk",
}

SKIP_SYMS = {"SOL", "WSOL", "USDC", "USDT", "USD1", "ETH", "WETH", "BTC", "WBTC", "JUP", "JLP", "JITOSOL", "MSOL", "BNSOL"}


def fnum(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def now_et():
    return dt.datetime.now(ET)


def iso_et(t=None):
    t = t or now_et()
    return t.isoformat(timespec="seconds")


def http_json(url, tries=3, timeout=30, data=None, headers=None, method=None):
    last = None
    hdrs = dict(UA)
    if headers:
        hdrs.update(headers)
    body = data if data is None or isinstance(data, (bytes, bytearray)) else data
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as f:
                raw = f.read()
                if not raw:
                    return None
                return json.loads(raw)
        except Exception as e:
            last = e
            if i < tries - 1:
                time.sleep(1.4 * (i + 1))
    raise last


def rpc(method, params, tries=3):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                RPC, data=body, headers={"content-type": "application/json", **UA}
            )
            with urllib.request.urlopen(req, timeout=30) as f:
                return json.load(f).get("result")
        except Exception as e:
            last = e
            if i < tries - 1:
                time.sleep(2 * (i + 1))
    raise last


def load_dotenv():
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip("'").strip('"')
        if k and k not in os.environ:
            os.environ[k] = v


def log_line(msg):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = msg.rstrip() + "\n"
    with open(LOG_PATH, "a") as f:
        f.write(line)
    # Wrapper already redirects stdout to scan.log; print only on a tty (manual runs).
    if sys.stdout.isatty():
        print(msg, flush=True)


# ---------------------------------------------------------------- collection
def _gt_row(p, src):
    a = p.get("attributes") or {}
    rel = (p.get("relationships") or {}).get("base_token", {}).get("data", {}) or {}
    tok = (rel.get("id") or "").split("_", 1)[-1]
    if not tok or tok in SKIP_MINTS:
        return None
    vol = a.get("volume_usd") or {}
    name = a.get("name") or ""
    sym = name.split("/")[0].strip() or "?"
    if sym.upper() in SKIP_SYMS:
        return None
    return {
        "token": tok,
        "symbol": sym,
        "pool": a.get("address"),
        "dex": ((p.get("relationships") or {}).get("dex", {}).get("data", {}) or {}).get("id"),
        "mc": fnum(a.get("market_cap_usd")),
        "fdv": fnum(a.get("fdv_usd")),
        "liq": fnum(a.get("reserve_in_usd")),
        "vol24": fnum(vol.get("h24")),
        "vol6": fnum(vol.get("h6")),
        "vol1": fnum(vol.get("h1")),
        "price": fnum(a.get("base_token_price_usd")),
        "created": a.get("pool_created_at"),
        "source": src,
        "src_gt": True,
    }


def _merge_row(found, rec):
    if not rec or not rec.get("token"):
        return
    prev = found.get(rec["token"])
    if prev is None:
        found[rec["token"]] = rec
        return
    if (rec.get("liq") or 0, rec.get("vol24") or 0) > (prev.get("liq") or 0, prev.get("vol24") or 0):
        srcs = []
        for s in ((prev.get("source") or ""), (rec.get("source") or "")):
            for part in str(s).split(","):
                if part and part not in srcs:
                    srcs.append(part)
        rec = dict(rec)
        rec["source"] = ",".join(srcs) or rec.get("source")
        for k in ("src_gt", "src_dex", "src_dex_profile", "src_new"):
            if prev.get(k) or rec.get(k):
                rec[k] = True
        if prev.get("created") and not rec.get("created"):
            rec["created"] = prev.get("created")
        if prev.get("pool") and not rec.get("pool"):
            rec["pool"] = prev.get("pool")
        found[rec["token"]] = rec
    else:
        srcs = []
        for s in ((prev.get("source") or ""), (rec.get("source") or "")):
            for part in str(s).split(","):
                if part and part not in srcs:
                    srcs.append(part)
        prev["source"] = ",".join(srcs) or prev.get("source")
        for k in ("src_gt", "src_dex", "src_dex_profile", "src_new"):
            if rec.get(k):
                prev[k] = True
        if rec.get("created") and not prev.get("created"):
            prev["created"] = rec.get("created")
        if rec.get("pool") and not prev.get("pool"):
            prev["pool"] = rec.get("pool")


def collect_gt():
    """High-volume Solana pools from GeckoTerminal. Stop once 24h vol falls below the floor."""
    found = {}

    def absorb(rows, src):
        kept_vol = 0
        for p in rows:
            rec = _gt_row(p, src)
            if not rec or not rec.get("pool"):
                continue
            if rec["vol24"] >= COLLECT_EARLY_VOL:
                kept_vol += 1
            _merge_row(found, rec)
        return kept_vol, len(rows)

    # Top 24h volume: early-exit once a full page is below the collection floor.
    below_pages = 0
    for page in range(1, 11):
        try:
            d = http_json(f"{GT}/pools?page={page}&sort=h24_volume_usd_desc")
        except Exception as e:
            print(f"  gt pools p{page} fail: {e}", flush=True)
            break
        rows = (d or {}).get("data") or []
        if not rows:
            break
        kept, n = absorb(rows, f"pools_vol_p{page}")
        print(f"  gt volume p{page}: {n} rows, loose-vol kept={kept}, uniq={len(found)}", flush=True)
        min_vol = min((fnum((p.get("attributes") or {}).get("volume_usd", {}).get("h24")) for p in rows), default=0)
        if min_vol < COLLECT_EARLY_VOL:
            below_pages += 1
            if below_pages >= 2:
                break
        time.sleep(0.3)

    for dur, pages in (("1h", 3), ("6h", 2)):
        for page in range(1, pages + 1):
            try:
                d = http_json(f"{GT}/trending_pools?duration={dur}&page={page}")
            except Exception as e:
                print(f"  gt trending {dur} p{page} fail: {e}", flush=True)
                break
            rows = (d or {}).get("data") or []
            if not rows:
                break
            absorb(rows, f"trending_{dur}_p{page}")
            time.sleep(0.3)
    return list(found.values())


def collect_gt_new_pools(pages=4):
    """Fresh Solana pools from GeckoTerminal new_pools (past ~48h, newest first)."""
    found = {}
    for page in range(1, pages + 1):
        try:
            d = http_json(f"{GT}/new_pools?page={page}")
        except Exception as e:
            print(f"  gt new_pools p{page} fail: {e}", flush=True)
            break
        rows = (d or {}).get("data") or []
        if not rows:
            break
        for p in rows:
            rec = _gt_row(p, f"new_pools_p{page}")
            if not rec:
                continue
            rec["src_new"] = True
            _merge_row(found, rec)
        print(f"  gt new_pools p{page}: {len(rows)} rows, uniq={len(found)}", flush=True)
        time.sleep(0.3)
    return list(found.values())


def collect_dex_profiles():
    """DexScreener latest token profiles, Solana only. Enriched later."""
    found = {}
    try:
        d = http_json(DEX_PROFILES, tries=2, timeout=25)
    except Exception as e:
        print(f"  dex profiles fail: {e}", flush=True)
        return []
    rows = d if isinstance(d, list) else (d or {}).get("data") or []
    for p in rows:
        if str(p.get("chainId") or "").lower() != "solana":
            continue
        tok = p.get("tokenAddress")
        if not tok or tok in SKIP_MINTS:
            continue
        found[tok] = {
            "token": tok,
            "symbol": "?",
            "pool": None,
            "dex": None,
            "mc": 0.0,
            "fdv": 0.0,
            "liq": 0.0,
            "vol24": 0.0,
            "vol6": 0.0,
            "vol1": 0.0,
            "price": 0.0,
            "created": None,
            "source": "dex_profiles",
            "src_dex_profile": True,
        }
    print(f"  dex profiles: solana={len(found)} of {len(rows)}", flush=True)
    return list(found.values())


def collect_universe():
    found = {}
    for rec in collect_gt():
        _merge_row(found, rec)
    new_rows = collect_gt_new_pools()
    for rec in new_rows:
        _merge_row(found, rec)
    for rec in collect_dex_profiles():
        _merge_row(found, rec)
    rows = list(found.values())
    return rows, len(new_rows)


def enrich_dexscreener(rows):
    """Overlay DexScreener mcap/liq/vol/price/age; prefer these for cheap gates."""
    by = {r["token"]: r for r in rows}
    toks = list(by)
    for i in range(0, len(toks), 30):
        chunk = toks[i : i + 30]
        url = DEX_TOKENS + ",".join(chunk)
        try:
            d = http_json(url, tries=2, timeout=25)
        except Exception as e:
            print(f"  dexscreener batch {i//30+1} fail: {e}", flush=True)
            time.sleep(0.3)
            continue
        pairs = (d or {}).get("pairs") or []
        best = {}
        for p in pairs:
            if (p.get("chainId") or "").lower() != "solana":
                continue
            mint = (p.get("baseToken") or {}).get("address")
            if not mint or mint in SKIP_MINTS:
                continue
            # Socials can live on a non-primary pair; ingest every info blob.
            ingest_dex_info(mint, p.get("info"))
            liq = fnum((p.get("liquidity") or {}).get("usd"))
            vol = fnum((p.get("volume") or {}).get("h24"))
            cur = best.get(mint)
            if cur is None or (liq, vol) > (cur[0], cur[1]):
                best[mint] = (liq, vol, p)
        # Batch succeeded: mints with no info still count as a known-empty Dex result.
        for mint in chunk:
            mark_dex_seen(mint)
        for mint, (_, _, p) in best.items():
            rec = by.get(mint)
            if rec is None:
                continue
            base = p.get("baseToken") or {}
            rec["symbol"] = base.get("symbol") or rec.get("symbol") or "?"
            rec["name"] = base.get("name") or rec.get("symbol")
            rec["price"] = fnum(p.get("priceUsd"), rec.get("price") or 0)
            rec["mc"] = fnum(p.get("marketCap") or p.get("fdv"), rec.get("mc") or 0)
            rec["fdv"] = fnum(p.get("fdv"), rec.get("fdv") or 0)
            rec["liq"] = fnum((p.get("liquidity") or {}).get("usd"), rec.get("liq") or 0)
            rec["vol24"] = fnum((p.get("volume") or {}).get("h24"), rec.get("vol24") or 0)
            rec["vol6"] = fnum((p.get("volume") or {}).get("h6"), rec.get("vol6") or 0)
            rec["vol1"] = fnum((p.get("volume") or {}).get("h1"), rec.get("vol1") or 0)
            rec["dex_pair"] = p.get("pairAddress")
            rec["dex"] = p.get("dexId") or rec.get("dex")
            rec["pair_created_ms"] = p.get("pairCreatedAt")
            rec["src_dex"] = True
            # Prefer the DexScreener primary pair when present.
            if p.get("pairAddress"):
                rec["pool"] = p.get("pairAddress")
        time.sleep(0.2)
    return list(by.values())


def cap_of(r):
    return r.get("mc") or r.get("fdv") or 0.0


def vl_of(r):
    liq = r.get("liq") or 0.0
    return (r.get("vol24") or 0.0) / liq if liq else 0.0


def turnover_of(r):
    cap = cap_of(r)
    return (r.get("vol24") or 0.0) / cap if cap else 0.0


def pool_age_seconds(r):
    created = r.get("created")
    if created:
        try:
            t = dt.datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=UTC)
            return (dt.datetime.now(UTC) - t.astimezone(UTC)).total_seconds()
        except Exception:
            pass
    ms = r.get("pair_created_ms")
    if ms:
        try:
            t = dt.datetime.fromtimestamp(float(ms) / 1000.0, UTC)
            return (dt.datetime.now(UTC) - t).total_seconds()
        except Exception:
            pass
    return None


def assign_lane(r):
    """Lane 2 if pool age is 15 min to 12 h; Lane 1 if aged or age unknown; None if <15 min."""
    age = pool_age_seconds(r)
    r["age_s"] = age
    r["turnover"] = turnover_of(r)
    if age is not None and age < AGE_L2_MIN_S:
        r["lane"] = None
        return None
    if age is not None and age < AGE_L2_MAX_S:
        r["lane"] = "l2"
        return "l2"
    r["lane"] = "l1"
    return "l1"


def cheap_numeric(rows):
    """Apply per-lane liquidity, volume, and turnover gates. Market cap is info-only."""
    staged = {"collected": len(rows), "liq": 0, "vol": 0, "too_fresh": 0, "l1": {}, "l2": {}}
    for lane in ("l1", "l2"):
        staged[lane] = {"candidates": 0, "liq": 0, "vol": 0}
    out = []
    for r in rows:
        lane = assign_lane(r)
        if lane is None:
            r["cheap_fail"] = f"younger than 15m (age_s={r.get('age_s')})"
            staged["too_fresh"] += 1
            continue
        staged[lane]["candidates"] += 1
        liq = r.get("liq") or 0.0
        vol = r.get("vol24") or 0.0
        turn = r.get("turnover") or 0.0
        cap = cap_of(r)
        reasons = []
        if lane == "l2":
            if liq < LIQ_LO:
                reasons.append(f"liq {liq:.0f} < {LIQ_LO:.0f}")
            if vol < VOL_L2:
                reasons.append(f"vol24 {vol:.0f} < {VOL_L2:.0f}")
            if cap <= 0:
                reasons.append("mcap missing (turnover unknown)")
            elif turn < TURN_L2:
                reasons.append(f"turnover {turn:.3f} < {TURN_L2}")
        else:
            if liq < LIQ_LO or liq > LIQ_HI_L1:
                reasons.append(f"liq {liq:.0f} not in {LIQ_LO:.0f}-{LIQ_HI_L1:.0f}")
            if vol < VOL_L1:
                reasons.append(f"vol24 {vol:.0f} < {VOL_L1:.0f}")
            if cap <= 0:
                reasons.append("mcap missing (turnover unknown)")
            elif turn < TURN_L1:
                reasons.append(f"turnover {turn:.3f} < {TURN_L1}")
        if reasons:
            r["cheap_fail"] = "; ".join(reasons)
            # Count how far they got for the funnel (liq pass, then vol+turnover).
            liq_ok = (liq >= LIQ_LO) if lane == "l2" else (LIQ_LO <= liq <= LIQ_HI_L1)
            if liq_ok:
                staged[lane]["liq"] += 1
                staged["liq"] += 1
            continue
        staged[lane]["liq"] += 1
        staged[lane]["vol"] += 1
        staged["liq"] += 1
        staged["vol"] += 1
        out.append(r)
    return out, staged


# ---------------------------------------------------------------- social presence
def reset_social_state():
    """Clear per-run social cache and Pump.fun backoff flag."""
    global _PUMP_DISABLED
    SOCIAL_CACHE.clear()
    _PUMP_DISABLED = False


def _empty_socials():
    return {
        "twitter": None,
        "telegram": None,
        "website": None,
        "flags": [],
        "source": None,
        "unknown": False,
    }


def _cache_entry(mint):
    ent = SOCIAL_CACHE.get(mint)
    if ent is None:
        ent = {"dex_seen": False, "pump_seen": False, "socials": _empty_socials(), "error": None}
        SOCIAL_CACHE[mint] = ent
    return ent


def _norm_host(host):
    host = (host or "").lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host


def _add_scheme(url):
    u = (url or "").strip()
    if not u:
        return ""
    if u.lower().startswith(("http://", "https://")):
        return u
    return "https://" + u.lstrip("/")


def classify_social_url(url):
    """Return (kind, normalized_url) where kind is twitter, telegram, or website.

    Bare @handles are treated as X. t.me paths without a scheme are Telegram.
    Returns (None, None) for empty or unusable values.
    """
    if url is None:
        return None, None
    u = str(url).strip()
    if not u or u.lower() in ("n/a", "none", "null", "-", "http://", "https://"):
        return None, None
    if u.startswith("@"):
        handle = u[1:].strip().lstrip("@").split()[0].strip("/")
        if handle:
            return "twitter", "https://x.com/" + handle
        return None, None
    low = u.lower()
    if low.startswith("t.me/") or low.startswith("telegram.me/") or low.startswith("telegram.dog/"):
        u = _add_scheme(u)
        return "telegram", u
    if not low.startswith(("http://", "https://")):
        # pump.fun sometimes stores a bare handle or domain.
        if "/" not in u and " " not in u and "." not in u:
            return "twitter", "https://x.com/" + u.lstrip("@")
        u = _add_scheme(u)
        low = u.lower()
    try:
        parsed = urllib.parse.urlparse(u)
    except Exception:
        return None, None
    host = _norm_host(parsed.netloc)
    if not host:
        return None, None
    if host in TWITTER_HOSTS:
        return "twitter", u
    if host in TELEGRAM_HOSTS:
        return "telegram", u
    return "website", u


def twitter_is_generic_or_status(url):
    """True when an X/Twitter link is a status, intent, or other non-profile URL."""
    kind, u = classify_social_url(url)
    if kind != "twitter" or not u:
        return False
    try:
        parsed = urllib.parse.urlparse(u)
    except Exception:
        return True
    host = _norm_host(parsed.netloc)
    if host in {"t.co"}:
        return True
    parts = [x for x in (parsed.path or "").split("/") if x]
    low_parts = [x.lower() for x in parts]
    if not low_parts:
        return True
    if "status" in low_parts or "statuses" in low_parts:
        return True
    # /i/communities/<id> is a real community presence, not generic.
    if low_parts[0] == "i" and len(low_parts) >= 2 and low_parts[1] == "communities":
        return len(low_parts) < 3
    if low_parts[0] in TWITTER_GENERIC_HEADS:
        return True
    return False


def twitter_identity(url):
    """Stable identity for reuse checks: x.com/<handle> or x.com/i/communities/<id>."""
    kind, u = classify_social_url(url)
    if kind != "twitter" or not u:
        return None
    try:
        parsed = urllib.parse.urlparse(u)
    except Exception:
        return None
    parts = [x for x in (parsed.path or "").split("/") if x]
    if not parts:
        return "x.com"
    low = [x.lower() for x in parts]
    if low[0] == "i" and len(low) >= 3 and low[1] == "communities":
        return "x.com/i/communities/" + low[2]
    handle = low[0]
    if handle in TWITTER_GENERIC_HEADS:
        # Keep the raw path so identical generic links still cluster.
        path = "/".join(low)
        return "x.com/" + path
    return "x.com/" + handle


def _set_kind(dst, kind, url):
    if not kind or not url:
        return
    if kind == "twitter" and not dst.get("twitter"):
        dst["twitter"] = url
    elif kind == "telegram" and not dst.get("telegram"):
        dst["telegram"] = url
    elif kind == "website" and not dst.get("website"):
        dst["website"] = url


def _merge_source(dst, src):
    prev = dst.get("source")
    if not src:
        return
    if not prev:
        dst["source"] = src
    elif src not in str(prev).split("+"):
        dst["source"] = "+".join([prev, src])


def ingest_links(mint, links, source):
    """Merge classified links into the per-mint cache. Does not mark unknown."""
    ent = _cache_entry(mint)
    socials = ent["socials"]
    for raw in links:
        kind, url = classify_social_url(raw)
        if kind == "website" and source == "socials_array":
            # Instagram / Discord / YouTube in the socials array are not a website bonus.
            continue
        _set_kind(socials, kind, url)
    if any(socials.get(k) for k in ("twitter", "telegram", "website")):
        _merge_source(socials, source if source != "socials_array" else "dexscreener")
    return ent


def ingest_dex_info(mint, info):
    if not mint or not isinstance(info, dict):
        return
    links = []
    for s in info.get("socials") or []:
        if isinstance(s, dict):
            links.append(s.get("url") or s.get("link"))
        elif isinstance(s, str):
            links.append(s)
    # Apply socials first, skipping non X/TG site-like entries in that array.
    ingest_links(mint, links, "socials_array")
    sites = []
    for w in info.get("websites") or []:
        if isinstance(w, dict):
            sites.append(w.get("url") or w.get("link"))
        elif isinstance(w, str):
            sites.append(w)
    ingest_links(mint, sites, "dexscreener")
    _merge_source(_cache_entry(mint)["socials"], "dexscreener")


def mark_dex_seen(mint):
    """A successful DexScreener batch included this mint (socials may still be empty)."""
    if not mint:
        return
    ent = _cache_entry(mint)
    ent["dex_seen"] = True
    if ent["socials"].get("unknown") and ent["error"] is None:
        ent["socials"]["unknown"] = False


def _social_score(socials):
    return int(bool(socials.get("twitter"))) + int(bool(socials.get("telegram"))) + int(bool(socials.get("website")))


def _public_socials(socials):
    return {
        "twitter": (socials or {}).get("twitter"),
        "telegram": (socials or {}).get("telegram"),
        "website": (socials or {}).get("website"),
    }


def fetch_dex_socials(mint):
    """Single-mint DexScreener lookup when the enrich batch missed this token."""
    ent = _cache_entry(mint)
    if ent["dex_seen"]:
        return ent
    last_err = None
    urls = [DEX_TOKENS + mint, DEX_TOKENS_V1 + mint]
    for url in urls:
        try:
            d = http_json(url, tries=2, timeout=20)
        except Exception as e:
            last_err = e
            continue
        rows = []
        if isinstance(d, dict):
            rows = d.get("pairs") or d.get("data") or []
        elif isinstance(d, list):
            rows = d
        for p in rows or []:
            if str(p.get("chainId") or "").lower() not in ("", "solana"):
                continue
            base = (p.get("baseToken") or {}).get("address") or mint
            ingest_dex_info(base or mint, p.get("info"))
        mark_dex_seen(mint)
        return ent
    ent["error"] = f"dex {last_err}"[:160] if last_err else "dex empty"
    return ent


def fetch_pump_socials(mint):
    """Pump.fun metadata fallback (twitter/telegram/website). Disabled after 403/401."""
    global _PUMP_DISABLED
    ent = _cache_entry(mint)
    if ent["pump_seen"] or _PUMP_DISABLED:
        if _PUMP_DISABLED and not ent["pump_seen"]:
            ent["error"] = (ent.get("error") or "pump disabled this run") 
        return ent
    last_err = None
    for tmpl in PUMP_COINS:
        try:
            d = http_json(tmpl.format(mint=mint), tries=1, timeout=12)
        except urllib.error.HTTPError as e:
            last_err = e
            if getattr(e, "code", None) in (401, 403):
                _PUMP_DISABLED = True
                ent["error"] = f"pump {e}"[:160]
                return ent
            continue
        except Exception as e:
            last_err = e
            continue
        ent["pump_seen"] = True
        if not isinstance(d, dict):
            return ent
        links = [d.get("twitter"), d.get("telegram"), d.get("website"), d.get("twitter_url"), d.get("telegram_url"), d.get("website_url")]
        ingest_links(mint, links, "pump")
        return ent
    if last_err is not None:
        ent["error"] = f"pump {last_err}"[:160]
    return ent


def resolve_socials(mint):
    """Fill cache for one mint. Dex first, Pump only if X and Telegram are both missing.

    Unknown only when Dex failed and Pump could not fill the gap.
    """
    ent = fetch_dex_socials(mint)
    socials = ent["socials"]
    if socials.get("twitter") or socials.get("telegram"):
        socials["unknown"] = False
        return ent
    # Website-only or empty: try Pump for an X/Telegram link.
    fetch_pump_socials(mint)
    socials = ent["socials"]
    if socials.get("twitter") or socials.get("telegram") or socials.get("website"):
        socials["unknown"] = False
        return ent
    if ent["dex_seen"]:
        # Dex answered; Pump miss does not turn a known-empty result into unknown.
        socials["unknown"] = False
        return ent
    socials["unknown"] = True
    return ent


def cheap_social(rows):
    """Require at least one X/Twitter or Telegram link. Website is a bonus, not enough alone.

    Generic/status X URLs and X links reused in this scan are flagged, not gated.
    API-unknown is fail-closed and logged as social_unknown.
    """
    out = []
    staged = {"social": 0, "social_fail": 0, "social_unknown": 0, "l1": {"social": 0, "social_fail": 0}, "l2": {"social": 0, "social_fail": 0}}
    # Resolve first so reuse can be computed across the whole vol-passer set.
    for r in rows:
        mint = r.get("token")
        try:
            ent = resolve_socials(mint)
        except Exception as e:
            ent = _cache_entry(mint)
            ent["error"] = f"social {e}"[:160]
            ent["socials"]["unknown"] = not ent["dex_seen"]
        socials = dict(ent["socials"])
        socials["flags"] = list(socials.get("flags") or [])
        r["socials"] = socials
        r["social_score"] = _social_score(socials)
        r["social_unknown"] = bool(socials.get("unknown"))
        if socials.get("twitter") and twitter_is_generic_or_status(socials["twitter"]):
            if "twitter_generic_or_status" not in socials["flags"]:
                socials["flags"].append("twitter_generic_or_status")
        time.sleep(0.05)

    reuse = {}
    for r in rows:
        ident = twitter_identity((r.get("socials") or {}).get("twitter"))
        if ident:
            reuse.setdefault(ident, []).append(r)
    for ident, group in reuse.items():
        if len({x.get("token") for x in group}) < 2:
            continue
        for r in group:
            flags = (r.get("socials") or {}).setdefault("flags", [])
            if "twitter_reused" not in flags:
                flags.append("twitter_reused")

    for r in rows:
        socials = r.get("socials") or _empty_socials()
        r["social_score"] = _social_score(socials)
        r["social_flags"] = list(socials.get("flags") or [])
        lane = r.get("lane")
        if socials.get("unknown"):
            r["social_fail"] = "social_unknown"
            r["social_unknown"] = True
            staged["social_fail"] += 1
            staged["social_unknown"] += 1
            if lane in ("l1", "l2"):
                staged[lane]["social_fail"] += 1
            continue
        if not socials.get("twitter") and not socials.get("telegram"):
            r["social_fail"] = "no X/Twitter or Telegram link"
            staged["social_fail"] += 1
            if lane in ("l1", "l2"):
                staged[lane]["social_fail"] += 1
            continue
        staged["social"] += 1
        if lane in ("l1", "l2"):
            staged[lane]["social"] += 1
        out.append(r)
    return out, staged


def too_young_l1(r):
    """True if the pair is known to be younger than 12 hours (Lane 1 should not fetch)."""
    age = r.get("age_s")
    if age is None:
        age = pool_age_seconds(r)
    if age is not None and age < MIN_CANDLES_L1 * 3600:
        return True
    return False


def fetch_candles(pool, limit=24):
    d = http_json(f"{GT}/pools/{pool}/ohlcv/hour?aggregate=1&limit={limit}&currency=usd")
    return ((d or {}).get("data") or {}).get("attributes", {}).get("ohlcv_list") or []


def cheap_candles(rows):
    out = []
    for r in rows:
        lane = r.get("lane") or "l1"
        need = MIN_CANDLES_L1 if lane == "l1" else MIN_CANDLES_L2
        if lane == "l1" and too_young_l1(r):
            r["candle_hours"] = 0
            r["candle_fail"] = "younger than 12h"
            continue
        pool = r.get("pool")
        if not pool:
            r["candle_fail"] = "no pool"
            continue
        try:
            cl = fetch_candles(pool, 24)
        except Exception as e:
            r["candle_fail"] = f"ohlcv {e}"[:80]
            time.sleep(0.25)
            continue
        r["candle_hours"] = len(cl or [])
        if len(cl or []) < need:
            r["candle_fail"] = f"only {len(cl or [])} hourly candles (need {need})"
        else:
            out.append(r)
        time.sleep(0.25)
    return out


# ---------------------------------------------------------------- RugCheck + on-chain
def rugcheck_report(mint, pool_addr):
    """Public RugCheck token report. Adjusts top-10 by excluding pool and AMM vaults."""
    d = http_json(RUGCHECK.format(mint=mint), tries=3, timeout=45)
    markets = d.get("markets") or []
    vaults = set()
    pool_pubkeys = set()
    for m in markets:
        pool_pubkeys.add(m.get("pubkey"))
        if m.get("pubkey") == pool_addr or pool_addr in (m.get("pubkey"),):
            for k in ("liquidityA", "liquidityB", "mintLP"):
                if m.get(k):
                    vaults.add(m[k])
        if m.get("mintB") == mint:
            for k in ("liquidityA", "liquidityB", "mintLP"):
                if m.get(k):
                    vaults.add(m[k])

    holders = d.get("topHolders") or []

    def is_vault(h):
        return (
            (h.get("address") in vaults)
            or (h.get("owner") in vaults)
            or (h.get("owner") in pool_pubkeys)
            or (h.get("address") in pool_pubkeys)
        )

    raw10 = sum(fnum(h.get("pct")) for h in holders[:10])
    filt = [h for h in holders if not is_vault(h)]
    adj10 = sum(fnum(h.get("pct")) for h in filt[:10])
    excluded = [
        {"addr": h.get("address"), "owner": h.get("owner"), "pct": fnum(h.get("pct"))}
        for h in holders[:12]
        if is_vault(h)
    ]

    ext = d.get("token_extensions") or {}
    tf = d.get("transferFee") or {}
    tfcfg = ext.get("transferFeeConfig") if isinstance(ext, dict) else None
    pool_tax_pct = fnum(tf.get("pct"))
    tax_pct = pool_tax_pct
    if tfcfg:
        try:
            bps = [fnum(tfcfg.get("transferFeeBasisPoints"))]
            for k in ("newerTransferFee", "olderTransferFee"):
                if isinstance(tfcfg.get(k), dict):
                    bps.append(fnum(tfcfg[k].get("transferFeeBasisPoints")))
            tax_pct = max(tax_pct, max(bps) / 100.0)
        except Exception:
            pass

    return {
        "raw10": raw10,
        "adj10": adj10,
        "excluded_vaults": excluded,
        "top3_adj": sum(fnum(h.get("pct")) for h in filt[:3]),
        "totalHolders": d.get("totalHolders"),
        "mintAuthority": d.get("mintAuthority"),
        "freezeAuthority": d.get("freezeAuthority"),
        "rugged": d.get("rugged"),
        "score_norm": d.get("score_normalised"),
        "pool_tax_pct": pool_tax_pct,
        "tax_pct": tax_pct,
        "transferFee_raw": tf,
        "token_extensions": ext,
        "risks": [
            {
                "name": r.get("name"),
                "value": r.get("value"),
                "desc": r.get("description"),
                "level": r.get("level"),
                "score": r.get("score"),
            }
            for r in (d.get("risks") or [])
        ],
        "markets": [
            {
                "pubkey": m.get("pubkey"),
                "lp_pct": (m.get("lp") or {}).get("lpLockedPct") if isinstance(m.get("lp"), dict) else None,
                "lp_locked": (m.get("lp") or {}).get("lpLocked") if isinstance(m.get("lp"), dict) else None,
            }
            for m in markets
        ],
        "creator": d.get("creator"),
        "tokenProgram": d.get("tokenProgram"),
    }


def onchain_mint(mint):
    r = rpc("getAccountInfo", [mint, {"encoding": "jsonParsed"}])
    v = (r or {}).get("value") or {}
    parsed = ((v.get("data") or {}).get("parsed") or {}) if isinstance(v.get("data"), dict) else {}
    info = parsed.get("info") or {}
    return {
        "program": (v.get("data") or {}).get("program") if isinstance(v.get("data"), dict) else None,
        "owner": v.get("owner"),
        "mintAuthority": info.get("mintAuthority"),
        "freezeAuthority": info.get("freezeAuthority"),
        "extensions": {e.get("extension"): e.get("state") for e in (info.get("extensions") or [])},
    }


def _bps_from_cfg(cfg):
    if not isinstance(cfg, dict):
        return None, None
    bps = []
    if cfg.get("transferFeeBasisPoints") is not None:
        bps.append(float(cfg["transferFeeBasisPoints"]))
    for k in ("newerTransferFee", "olderTransferFee"):
        if isinstance(cfg.get(k), dict) and cfg[k].get("transferFeeBasisPoints") is not None:
            bps.append(float(cfg[k]["transferFeeBasisPoints"]))
    auth = cfg.get("transferFeeConfigAuthority")
    return (max(bps) if bps else 0.0), auth


def hidden_fee(rc, onchain=None):
    reported = fnum(((rc or {}).get("transferFee_raw") or {}).get("pct"))
    rc_bps, rc_auth = _bps_from_cfg(((rc or {}).get("token_extensions") or {}).get("transferFeeConfig"))
    oc_ext = (onchain or {}).get("extensions") or {}
    oc_bps, oc_auth = _bps_from_cfg(oc_ext.get("transferFeeConfig"))
    srcs = [b for b in (rc_bps, oc_bps) if b is not None]
    fee_bps = max(srcs) if srcs else 0.0
    real = max(reported, fee_bps / 100.0)
    auth = oc_auth if oc_auth is not None else rc_auth
    has_cfg = (rc_bps is not None) or (oc_bps is not None)
    auth_live = bool(has_cfg and auth not in NULL_KEYS)
    hook = oc_ext.get("transferHook") or ((rc or {}).get("token_extensions") or {}).get("transferHook")
    hook_prog = (hook or {}).get("programId") if isinstance(hook, dict) else None
    flags = []
    if real > reported + 1e-9:
        flags.append(f"HIDDEN FEE {fee_bps:.0f} bps vs pool-reported {reported:.2f}%")
    if auth_live:
        flags.append(f"fee authority LIVE ({auth})")
    if hook_prog not in NULL_KEYS:
        flags.append(f"transferHook program {hook_prog}")
    ok_tax = real < TAX_FAIL_PCT
    ok_auth = (not auth_live) and (hook_prog in NULL_KEYS)
    return {
        "reported_tax_pct": reported,
        "fee_bps": fee_bps,
        "real_tax_pct": real,
        "fee_authority": auth,
        "fee_authority_live": auth_live,
        "transfer_hook": hook_prog,
        "pass": ok_tax and ok_auth,
        "flags": flags,
    }


def _live_auth(val):
    return val not in NULL_KEYS


def lp_locked_pct(rc, pool):
    mk = [m for m in (rc.get("markets") or []) if m.get("pubkey") == pool]
    if mk and mk[0].get("lp_pct") is not None:
        return fnum(mk[0].get("lp_pct"))
    vals = [m.get("lp_pct") for m in (rc.get("markets") or []) if m.get("lp_pct") is not None]
    return max((fnum(v) for v in vals), default=None)


def antirug(r, rc, oc, hf):
    """Hard fails for mint/freeze, LP, honeypot, pause, tax, proxy/fee authority, RugCheck dangers."""
    fails = []
    mint = (oc or {}).get("mintAuthority") if oc else None
    frz = (oc or {}).get("freezeAuthority") if oc else None
    if mint is None:
        mint = rc.get("mintAuthority")
    if frz is None:
        frz = rc.get("freezeAuthority")
    if _live_auth(mint):
        fails.append("mint authority live")
    if _live_auth(frz):
        fails.append("freeze authority live")

    lp = lp_locked_pct(rc, r.get("pool"))
    if lp is None or lp < LP_MIN_PCT:
        fails.append(f"LP only {0 if lp is None else lp:.0f}% locked/burned")

    ext = rc.get("token_extensions") or {}
    oce = (oc or {}).get("extensions") or {}
    if ext.get("pausableConfig") or oce.get("pausableConfig"):
        fails.append("pausable token")
    if ext.get("nonTransferable") or oce.get("nonTransferable"):
        fails.append("non-transferable")
    das = ext.get("defaultAccountState") or oce.get("defaultAccountState")
    if das and "frozen" in json.dumps(das).lower():
        fails.append("default account state frozen")
    if ext.get("permanentDelegate") or oce.get("permanentDelegate"):
        fails.append("permanent delegate (proxy ownership)")

    if rc.get("rugged"):
        fails.append("RugCheck rugged=true")
    dangers = []
    for rk in rc.get("risks") or []:
        nm = (rk.get("name") or "").lower()
        level = (rk.get("level") or "").lower()
        if level == "danger" or any(
            k in nm for k in ("honeypot", "rugged", "freeze", "mint authority", "copycat", "lp unlocked")
        ):
            dangers.append(rk.get("name") or nm)
            fails.append(f"RugCheck danger: {rk.get('name')}")
    if not hf.get("pass"):
        if (hf.get("real_tax_pct") or 0) >= TAX_FAIL_PCT:
            fails.append(f"real tax {hf['real_tax_pct']:.2f}% >= 5%")
        if hf.get("fee_authority_live"):
            fails.append("live fee authority")
        if hf.get("transfer_hook") not in NULL_KEYS:
            fails.append("transfer hook (proxy fee logic)")

    checks = {
        "mint": "revoked" if not _live_auth(mint) else "live",
        "freeze": "revoked" if not _live_auth(frz) else "live",
        "lp_pct": None if lp is None else round(lp, 2),
        "honeypot": "no" if not any("honeypot" in (x or "").lower() for x in dangers) else "yes",
        "paused": "no" if not any("pausable" in f or "frozen" in f or "non-transferable" in f for f in fails) else "yes",
        "tax_pct": round(hf.get("real_tax_pct") or 0, 4),
        "fee_authority": "none" if not hf.get("fee_authority_live") else "live",
        "adj10": None if rc.get("adj10") is None else round(rc["adj10"], 2),
        "rugcheck_dangers": dangers,
    }
    # unique fails, stable order
    seen = set()
    uniq = []
    for f in fails:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return uniq, checks


def cheap_adj10_and_security(rows):
    """RugCheck + anti-rug/hidden-fee. adj10 is recorded and shadow-logged, not a gate."""
    scored = []
    full_pass = []
    for r in rows:
        try:
            rc = rugcheck_report(r["token"], r.get("pool"))
        except Exception as e:
            r["adj10_fail"] = f"rugcheck {e}"[:120]
            r["antirug_fails"] = [f"rugcheck {e}"[:120]]
            time.sleep(0.5)
            continue
        r["rc"] = rc
        adj = rc.get("adj10")
        if adj is None:
            r["adj10_shadow"] = "adj10 missing"
        else:
            r["adj10"] = adj
            if adj > ADJ10_MAX:
                r["adj10_shadow"] = f"adj10 {adj:.1f}% > {ADJ10_MAX:.0f}% (shadow only, not a gate)"
            else:
                r["adj10_shadow"] = "ok"
        scored.append(r)

        try:
            oc = onchain_mint(r["token"])
        except Exception as e:
            oc = None
            r["onchain_err"] = str(e)[:80]
        hf = hidden_fee(rc, oc)
        r["onchain"] = oc
        r["hidden_fee"] = hf
        fails, checks = antirug(r, rc, oc, hf)
        r["antirug_fails"] = fails
        r["checks"] = checks
        if not fails:
            full_pass.append(r)
        time.sleep(0.55)
    return scored, full_pass


# ---------------------------------------------------------------- state / webhook / shadow
def load_alerted():
    if not ALERT_STATE.exists():
        return {}
    try:
        return json.loads(ALERT_STATE.read_text())
    except Exception:
        return {}


def save_alerted(state):
    cutoff = now_et() - dt.timedelta(hours=DEDUPE_HOURS)
    cleaned = {}
    for mint, ts in state.items():
        try:
            t = dt.datetime.fromisoformat(ts)
            if t.tzinfo is None:
                t = t.replace(tzinfo=ET)
            if t >= cutoff:
                cleaned[mint] = ts
        except Exception:
            continue
    ALERT_STATE.write_text(json.dumps(cleaned, indent=1))
    return cleaned


def dedupe(passers):
    state = save_alerted(load_alerted())
    cutoff = now_et() - dt.timedelta(hours=DEDUPE_HOURS)
    fresh = []
    for r in passers:
        ts = state.get(r["token"])
        if ts:
            try:
                t = dt.datetime.fromisoformat(ts)
                if t.tzinfo is None:
                    t = t.replace(tzinfo=ET)
                if t >= cutoff:
                    r["deduped"] = ts
                    continue
            except Exception:
                pass
        fresh.append(r)
    return fresh, state


def payload_coin(r, ts):
    return {
        "mint": r["token"],
        "symbol": r.get("symbol") or "?",
        "price": r.get("price") or 0,
        "mcap": cap_of(r),
        "liq": r.get("liq") or 0,
        "vol": r.get("vol24") or 0,
        "lane": r.get("lane"),
        "socials": _public_socials(r.get("socials") or {}),
        "social_score": r.get("social_score") if r.get("social_score") is not None else _social_score(r.get("socials") or {}),
        "checks": r.get("checks") or {},
        "timestamp": ts,
    }


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
    body = json.dumps({"timestamp": ts, "passers": [payload_coin(r, ts) for r in passers]}).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "x-webhook-key": key,
    }
    try:
        http_json(url, tries=2, timeout=20, data=body, headers=headers, method="POST")
        return "posted"
    except Exception as e:
        log_line(f"{ts} webhook POST failed: {e}")
        return f"error:{e}"[:160]


def mark_alerted(passers, state, ts):
    for r in passers:
        state[r["token"]] = ts
    save_alerted(state)


def _shadow_record(r, ts, passed=False):
    rc = r.get("rc") or {}
    reasons = []
    if r.get("cheap_fail"):
        reasons.append(r["cheap_fail"])
    if r.get("social_fail"):
        reasons.append(r["social_fail"])
    if r.get("social_unknown") and "social_unknown" not in reasons:
        reasons.append("social_unknown")
    flags = r.get("social_flags") or (r.get("socials") or {}).get("flags") or []
    for fl in flags:
        if fl not in reasons:
            reasons.append(fl)
    if r.get("candle_fail"):
        reasons.append(r["candle_fail"])
    if r.get("adj10_shadow") and r.get("adj10_shadow") not in ("ok", None):
        reasons.append(r["adj10_shadow"])
    if r.get("adj10_fail"):
        reasons.append(r["adj10_fail"])
    if r.get("antirug_fails"):
        reasons.extend(r["antirug_fails"])
    if passed:
        status = "pass"
    elif r.get("antirug_fails") or r.get("adj10_fail"):
        status = "antirug_fail"
    elif r.get("candle_fail"):
        status = "candle_fail"
    elif r.get("social_unknown"):
        status = "social_unknown"
    elif r.get("social_fail"):
        status = "social_fail"
    elif r.get("cheap_fail"):
        status = "cheap_fail"
    else:
        status = "other"
    socials = r.get("socials") or {}
    return {
        "ts": ts,
        "mint": r.get("token"),
        "symbol": r.get("symbol") or "?",
        "lane": r.get("lane"),
        "liq": r.get("liq") or 0,
        "vol24": r.get("vol24") or 0,
        "mcap": cap_of(r),
        "turnover": r.get("turnover") if r.get("turnover") is not None else turnover_of(r),
        "age_s": r.get("age_s"),
        "candles": r.get("candle_hours"),
        "holders": rc.get("totalHolders"),
        "raw10": rc.get("raw10"),
        "adj10": r.get("adj10") if r.get("adj10") is not None else rc.get("adj10"),
        "socials": _public_socials(socials),
        "social_score": r.get("social_score") if r.get("social_score") is not None else _social_score(socials),
        "social_flags": list(flags),
        "passed": bool(passed),
        "status": status,
        "reasons": reasons,
    }


def write_shadow(rows, passers, ts):
    """Append one compact record per candidate (liq, holders, top-10, lane, pass/fail)."""
    passer_mints = {r["token"] for r in passers}
    try:
        with open(SHADOW_PATH, "a") as f:
            for r in rows:
                rec = _shadow_record(r, ts, passed=r.get("token") in passer_mints)
                f.write(json.dumps(rec, default=str) + "\n")
    except Exception as e:
        log_line(f"{ts} shadow_log write failed: {e}")


# ---------------------------------------------------------------- run
def _empty_lane():
    return {
        "candidates": 0,
        "liq": 0,
        "vol": 0,
        "social": 0,
        "social_fail": 0,
        "candles": 0,
        "adj10_shadow": 0,
        "adj10_flagged": 0,
        "antirug": 0,
    }


def run(post=True):
    t0 = time.time()
    ts = iso_et()
    reset_social_state()
    staged = {
        "collected": 0,
        "new_pools": 0,
        "too_fresh": 0,
        "liq": 0,
        "vol": 0,
        "social": 0,
        "social_fail": 0,
        "social_unknown": 0,
        "candles": 0,
        "adj10_shadow": 0,
        "adj10_flagged": 0,
        "antirug": 0,
        "new": 0,
        "posted": 0,
        "skipped_position": 0,
        "l1": _empty_lane(),
        "l2": _empty_lane(),
    }

    if POSITION_FLAG.exists():
        staged["skipped_position"] = 1
        runtime = time.time() - t0
        log_line(
            f"{ts} skipped_position=1 collected=0 liq=0 vol=0 social=0 candles=0 adj10_shadow=0 "
            f"antirug=0 new=0 posted=0 runtime_s={runtime:.1f}"
        )
        return {"skipped_position": True, "runtime_s": runtime, "staged": staged, "passers": []}

    rows, n_new = collect_universe()
    staged["new_pools"] = n_new
    rows = enrich_dexscreener(rows)
    numeric, counts = cheap_numeric(rows)
    staged["collected"] = counts.get("collected", len(rows))
    staged["too_fresh"] = counts.get("too_fresh", 0)
    staged["liq"] = counts.get("liq", 0)
    staged["vol"] = counts.get("vol", 0)
    for lane in ("l1", "l2"):
        staged[lane]["candidates"] = counts.get(lane, {}).get("candidates", 0)
        staged[lane]["liq"] = counts.get(lane, {}).get("liq", 0)
        staged[lane]["vol"] = counts.get(lane, {}).get("vol", 0)

    social_ok, social_counts = cheap_social(numeric)
    staged["social"] = social_counts.get("social", 0)
    staged["social_fail"] = social_counts.get("social_fail", 0)
    staged["social_unknown"] = social_counts.get("social_unknown", 0)
    for lane in ("l1", "l2"):
        staged[lane]["social"] = social_counts.get(lane, {}).get("social", 0)
        staged[lane]["social_fail"] = social_counts.get(lane, {}).get("social_fail", 0)

    candle_ok = cheap_candles(social_ok)
    staged["candles"] = len(candle_ok)
    for r in candle_ok:
        if r.get("lane") in ("l1", "l2"):
            staged[r["lane"]]["candles"] += 1
    print(
        f"  cheap gates: collected={staged['collected']} new_pools={staged['new_pools']} "
        f"liq={staged['liq']} vol={staged['vol']} social={staged['social']} "
        f"social_fail={staged['social_fail']} "
        f"l1 vol={staged['l1']['vol']} social={staged['l1']['social']} "
        f"l2 vol={staged['l2']['vol']} social={staged['l2']['social']} candles pending",
        flush=True,
    )
    scored, full_ok = cheap_adj10_and_security(candle_ok)
    staged["adj10_shadow"] = len(scored)
    staged["adj10_flagged"] = sum(
        1 for r in scored if (r.get("adj10") is not None and r.get("adj10") > ADJ10_MAX)
    )
    staged["antirug"] = len(full_ok)
    for r in scored:
        lane = r.get("lane")
        if lane in ("l1", "l2"):
            staged[lane]["adj10_shadow"] += 1
            if r.get("adj10") is not None and r.get("adj10") > ADJ10_MAX:
                staged[lane]["adj10_flagged"] += 1
    for r in full_ok:
        if r.get("lane") in ("l1", "l2"):
            staged[r["lane"]]["antirug"] += 1

    fresh, state = dedupe(full_ok)
    staged["new"] = len(fresh)

    status = post_webhook(fresh, ts, disabled=not post)
    if status == "posted":
        staged["posted"] = len(fresh)
        mark_alerted(fresh, state, ts)
    elif status in ("disabled", "missing_env") and fresh:
        # Manual/test runs still record alerts only when a real POST happens.
        staged["posted"] = 0

    write_shadow(rows, full_ok, ts)

    runtime = time.time() - t0
    staged["runtime_s"] = round(runtime, 2)
    log_line(
        f"{ts} collected={staged['collected']} new_pools={staged['new_pools']} "
        f"liq={staged['liq']} vol={staged['vol']} social={staged['social']} "
        f"social_fail={staged['social_fail']} social_unknown={staged['social_unknown']} "
        f"candles={staged['candles']} "
        f"adj10_shadow={staged['adj10_shadow']} adj10_flagged={staged['adj10_flagged']} "
        f"antirug={staged['antirug']} new={staged['new']} posted={staged['posted']} "
        f"l1={staged['l1']['candidates']}/{staged['l1']['liq']}/{staged['l1']['vol']}/"
        f"{staged['l1']['social']}/{staged['l1']['candles']}/{staged['l1']['antirug']} "
        f"l2={staged['l2']['candidates']}/{staged['l2']['liq']}/{staged['l2']['vol']}/"
        f"{staged['l2']['social']}/{staged['l2']['candles']}/{staged['l2']['antirug']} "
        f"skipped_position={staged['skipped_position']} runtime_s={runtime:.1f} webhook={status}"
    )
    print(
        f"  FUNNEL collected={staged['collected']} new_pools={staged['new_pools']} too_fresh={staged['too_fresh']}\n"
        f"    L1: cand={staged['l1']['candidates']} liq={staged['l1']['liq']} vol={staged['l1']['vol']} "
        f"social={staged['l1']['social']} social_fail={staged['l1']['social_fail']} "
        f"candles={staged['l1']['candles']} adj10_shadow={staged['l1']['adj10_shadow']} "
        f"adj10_flagged={staged['l1']['adj10_flagged']} antirug={staged['l1']['antirug']}\n"
        f"    L2: cand={staged['l2']['candidates']} liq={staged['l2']['liq']} vol={staged['l2']['vol']} "
        f"social={staged['l2']['social']} social_fail={staged['l2']['social_fail']} "
        f"candles={staged['l2']['candles']} adj10_shadow={staged['l2']['adj10_shadow']} "
        f"adj10_flagged={staged['l2']['adj10_flagged']} antirug={staged['l2']['antirug']}\n"
        f"    social={staged['social']} social_fail={staged['social_fail']} "
        f"social_unknown={staged['social_unknown']} "
        f"new={staged['new']} posted={staged['posted']} webhook={status} runtime_s={runtime:.1f}",
        flush=True,
    )

    summary = {
        "timestamp": ts,
        "staged": staged,
        "webhook": status,
        "runtime_s": runtime,
        "numeric": [
            {
                "mint": r["token"],
                "symbol": r.get("symbol"),
                "lane": r.get("lane"),
                "mcap": cap_of(r),
                "liq": r.get("liq"),
                "vol": r.get("vol24"),
                "turnover": round(r.get("turnover") or turnover_of(r), 3),
                "vl": round(vl_of(r), 2),
                "social_score": r.get("social_score"),
                "socials": _public_socials(r.get("socials") or {}),
            }
            for r in numeric
        ],
        "passers": [payload_coin(r, ts) for r in full_ok],
        "fresh": [payload_coin(r, ts) for r in fresh],
        "social_fails": [
            {
                "mint": r["token"],
                "symbol": r.get("symbol"),
                "lane": r.get("lane"),
                "reason": r.get("social_fail"),
                "social_score": r.get("social_score"),
                "socials": _public_socials(r.get("socials") or {}),
                "flags": r.get("social_flags") or [],
            }
            for r in numeric
            if r.get("social_fail")
        ],
        "candle_fails": [
            {"mint": r["token"], "symbol": r.get("symbol"), "lane": r.get("lane"), "reason": r.get("candle_fail")}
            for r in social_ok
            if r.get("candle_fail")
        ],
        "adj10_shadow_flags": [
            {
                "mint": r["token"],
                "symbol": r.get("symbol"),
                "lane": r.get("lane"),
                "adj10": r.get("adj10"),
                "note": r.get("adj10_shadow"),
            }
            for r in scored
            if r.get("adj10") is not None and r.get("adj10") > ADJ10_MAX
        ],
        "antirug_fails": [
            {
                "mint": r["token"],
                "symbol": r.get("symbol"),
                "lane": r.get("lane"),
                "adj10": r.get("adj10"),
                "fails": r.get("antirug_fails"),
            }
            for r in scored
            if r.get("antirug_fails")
        ],
    }
    try:
        LAST_PATH.write_text(json.dumps(summary, indent=1, default=str))
    except Exception:
        pass
    return summary


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    load_dotenv()
    post = True
    if "--no-post" in argv:
        post = False
        argv.remove("--no-post")
    if os.environ.get("LITE_SCAN_NO_POST", "").lower() in ("1", "true", "yes"):
        post = False
    if argv and argv[0] not in ("--once", "--run"):
        print("usage: scan_lite.py [--once] [--no-post]", file=sys.stderr)
        return 2
    run(post=post)
    return 0


if __name__ == "__main__":
    sys.exit(main())
