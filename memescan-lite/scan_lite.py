#!/usr/bin/env python3
"""Lightweight Solana meme-coin scanner.

Read-only. Never signs a transaction, never touches a wallet, never trades.
No LLM calls. Standard library only.

Cheap gates (screener data first: GeckoTerminal + DexScreener):
  - market cap $250K-$1M
  - liquidity $150K-$1M
  - 24h volume >= $1.5M and 7-20x liquidity
  - at least 12 hourly candles
  - adjusted top-10 holders <= 30% (pool/AMM vaults excluded)

Only coins that pass every cheap gate get anti-rug + hidden-fee checks,
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
import urllib.request
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc

GT = "https://api.geckoterminal.com/api/v2/networks/solana"
DEX_TOKENS = "https://api.dexscreener.com/latest/dex/tokens/"
RUGCHECK = "https://api.rugcheck.xyz/v1/tokens/{mint}/report"
RPC = "https://api.mainnet-beta.solana.com"
UA = {"User-Agent": "memescan-lite/1.0", "accept": "application/json"}

MC_LO, MC_HI = 250_000, 1_000_000
LIQ_LO, LIQ_HI = 150_000, 1_000_000
VOL_LO = 1_500_000
VL_LO, VL_HI = 7.0, 20.0
MIN_CANDLES = 12
LP_MIN_PCT = 90.0
TAX_FAIL_PCT = 5.0
ADJ10_MAX = 30.0
DEDUPE_HOURS = 6
POSITION_FLAG = BASE / "POSITION_OPEN"
ALERT_STATE = BASE / "alerted.json"
LOG_PATH = BASE / "scan.log"
LAST_PATH = BASE / "last_result.json"
ENV_PATH = BASE / ".env"

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


def collect_gt():
    """High-volume Solana pools from GeckoTerminal. Stop once 24h vol falls below the floor."""
    found = {}

    def absorb(rows, src):
        kept_vol = 0
        for p in rows:
            rec = _gt_row(p, src)
            if not rec or not rec.get("pool"):
                continue
            if rec["vol24"] >= VOL_LO * 0.8:  # loose net; tight gate comes later
                kept_vol += 1
            prev = found.get(rec["token"])
            if prev is None or (rec["liq"], rec["vol24"]) > (prev["liq"], prev["vol24"]):
                found[rec["token"]] = rec
        return kept_vol, len(rows)

    # Top 24h volume: early-exit once a full page is below the volume floor.
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
        if min_vol < VOL_LO:
            below_pages += 1
            if below_pages >= 2:
                break
        time.sleep(0.25)

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
            time.sleep(0.25)
    return list(found.values())


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
            liq = fnum((p.get("liquidity") or {}).get("usd"))
            vol = fnum((p.get("volume") or {}).get("h24"))
            cur = best.get(mint)
            if cur is None or (liq, vol) > (cur[0], cur[1]):
                best[mint] = (liq, vol, p)
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


def cheap_numeric(rows):
    staged = {"collected": len(rows)}
    mcap = [r for r in rows if MC_LO <= cap_of(r) <= MC_HI]
    staged["mcap"] = len(mcap)
    liq = [r for r in mcap if LIQ_LO <= (r.get("liq") or 0) <= LIQ_HI]
    staged["liq"] = len(liq)
    vol = [r for r in liq if (r.get("vol24") or 0) >= VOL_LO and VL_LO <= vl_of(r) <= VL_HI]
    staged["vol"] = len(vol)
    return vol, staged


def too_young(r):
    """True if the pair is known to be younger than 12 hours (skip candle fetch)."""
    created = r.get("created")
    if created:
        try:
            t = dt.datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            if (dt.datetime.now(UTC) - t).total_seconds() < MIN_CANDLES * 3600:
                return True
        except Exception:
            pass
    ms = r.get("pair_created_ms")
    if ms:
        try:
            t = dt.datetime.fromtimestamp(float(ms) / 1000.0, UTC)
            if (dt.datetime.now(UTC) - t).total_seconds() < MIN_CANDLES * 3600:
                return True
        except Exception:
            pass
    return False


def fetch_candles(pool, limit=24):
    d = http_json(f"{GT}/pools/{pool}/ohlcv/hour?aggregate=1&limit={limit}&currency=usd")
    return ((d or {}).get("data") or {}).get("attributes", {}).get("ohlcv_list") or []


def cheap_candles(rows):
    out = []
    for r in rows:
        if too_young(r):
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
        if len(cl or []) < MIN_CANDLES:
            r["candle_fail"] = f"only {len(cl or [])} hourly candles"
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
    """RugCheck + adj10 cheap gate, then anti-rug/hidden-fee only on adj10 passers."""
    adj_pass = []
    full_pass = []
    for r in rows:
        try:
            rc = rugcheck_report(r["token"], r.get("pool"))
        except Exception as e:
            r["adj10_fail"] = f"rugcheck {e}"[:120]
            time.sleep(0.5)
            continue
        r["rc"] = rc
        adj = rc.get("adj10")
        if adj is None:
            r["adj10_fail"] = "adj10 missing"
            time.sleep(0.5)
            continue
        r["adj10"] = adj
        if adj > ADJ10_MAX:
            r["adj10_fail"] = f"adj10 {adj:.1f}% > {ADJ10_MAX:.0f}%"
            time.sleep(0.5)
            continue
        adj_pass.append(r)

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
    return adj_pass, full_pass


# ---------------------------------------------------------------- state / webhook
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


# ---------------------------------------------------------------- run
def run(post=True):
    t0 = time.time()
    ts = iso_et()
    staged = {
        "collected": 0,
        "mcap": 0,
        "liq": 0,
        "vol": 0,
        "candles": 0,
        "adj10": 0,
        "antirug": 0,
        "new": 0,
        "posted": 0,
        "skipped_position": 0,
    }

    if POSITION_FLAG.exists():
        staged["skipped_position"] = 1
        runtime = time.time() - t0
        log_line(
            f"{ts} skipped_position=1 collected=0 mcap=0 liq=0 vol=0 candles=0 adj10=0 "
            f"antirug=0 new=0 posted=0 runtime_s={runtime:.1f}"
        )
        return {"skipped_position": True, "runtime_s": runtime, "staged": staged, "passers": []}

    rows = collect_gt()
    rows = enrich_dexscreener(rows)
    numeric, counts = cheap_numeric(rows)
    staged.update(counts)
    candle_ok = cheap_candles(numeric)
    staged["candles"] = len(candle_ok)
    print(f"  cheap gates: collected={staged['collected']} mcap={staged['mcap']} liq={staged['liq']} vol={staged['vol']} candles pending", flush=True)
    adj_ok, full_ok = cheap_adj10_and_security(candle_ok)
    staged["adj10"] = len(adj_ok)
    staged["antirug"] = len(full_ok)
    fresh, state = dedupe(full_ok)
    staged["new"] = len(fresh)

    status = post_webhook(fresh, ts, disabled=not post)
    if status == "posted":
        staged["posted"] = len(fresh)
        mark_alerted(fresh, state, ts)
    elif status in ("disabled", "missing_env") and fresh:
        # Manual/test runs still record alerts only when a real POST happens.
        staged["posted"] = 0

    runtime = time.time() - t0
    staged["runtime_s"] = round(runtime, 2)
    log_line(
        f"{ts} collected={staged['collected']} mcap={staged['mcap']} liq={staged['liq']} "
        f"vol={staged['vol']} candles={staged['candles']} adj10={staged['adj10']} "
        f"antirug={staged['antirug']} new={staged['new']} posted={staged['posted']} "
        f"skipped_position={staged['skipped_position']} runtime_s={runtime:.1f} webhook={status}"
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
                "mcap": cap_of(r),
                "liq": r.get("liq"),
                "vol": r.get("vol24"),
                "vl": round(vl_of(r), 2),
            }
            for r in numeric
        ],
        "passers": [payload_coin(r, ts) for r in full_ok],
        "fresh": [payload_coin(r, ts) for r in fresh],
        "candle_fails": [
            {"mint": r["token"], "symbol": r.get("symbol"), "reason": r.get("candle_fail")}
            for r in numeric
            if r.get("candle_fail")
        ],
        "adj10_fails": [
            {
                "mint": r["token"],
                "symbol": r.get("symbol"),
                "adj10": r.get("adj10"),
                "reason": r.get("adj10_fail"),
            }
            for r in candle_ok
            if r.get("adj10_fail")
        ],
        "antirug_fails": [
            {
                "mint": r["token"],
                "symbol": r.get("symbol"),
                "adj10": r.get("adj10"),
                "fails": r.get("antirug_fails"),
            }
            for r in adj_ok
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
