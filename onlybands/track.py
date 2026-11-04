#!/usr/bin/env python3
"""Daily callout tracking for the OnlyBands pinned channels.

Merges any new messages dropped in inbox/*.jsonl into raw/, re-runs the rule-based
play extraction from build_backtest.py, and prints a running record:

  1. what the trader CLAIMED  (their own stated percentages)
  2. what the UNDERLYING actually did (verified from Yahoo 1-minute bars)

Run: /usr/bin/python3 /workspace/onlybands/track.py [--days N] [--today-only]
"""
import json, os, re, sys, glob, datetime as dt, urllib.request
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import build_backtest as bb

NY = dt.timezone(dt.timedelta(hours=-5))
CH_FILE = {"odte-iwm-jaycee-trades": "iwm-jaycee.jsonl",
           "odte-qqq-hipp-trades": "qqq-hipp.jsonl",
           "bucky-budget-swings": "bucky-budget.jsonl",
           "teej-breakout-trades": "teej-breakout.jsonl"}
LABEL = {"odte-iwm-jaycee-trades": "Jaycee (IWM)", "odte-qqq-hipp-trades": "Hipp (QQQ)",
         "bucky-budget-swings": "Bucky (swings)", "teej-breakout-trades": "Teej (breakout)"}

def merge_inbox():
    moved = []
    for f in sorted(glob.glob(os.path.join(BASE, "inbox", "*.jsonl"))):
        name = os.path.basename(f)
        ch = next((c for c, fn in CH_FILE.items() if name.startswith(c) or name.startswith(fn[:-6])), None)
        dest = os.path.join(BASE, "raw", CH_FILE.get(ch, name))
        seen = set()
        if os.path.exists(dest):
            for line in open(dest, encoding="utf-8"):
                try: m = json.loads(line)
                except Exception: continue
                seen.add((m.get("ts"), (m.get("text") or "")[:80]))
        rows = []
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line: continue
            try: m = json.loads(line)
            except Exception: continue
            if (m.get("ts"), (m.get("text") or "")[:80]) in seen: continue
            m.setdefault("channel", ch)
            rows.append(m); seen.add((m.get("ts"), (m.get("text") or "")[:80]))
        if rows:
            with open(dest, "a", encoding="utf-8") as out:
                for m in rows: out.write(json.dumps(m, ensure_ascii=False) + "\n")
            moved.append((ch, len(rows)))
        os.remove(f)
    return moved

# ---------- conditional calls (Jaycee's "hold only" format) ----------
COND = re.compile(r"\b(hold only|only|under this call|invalid|no hold|as long as)\b", re.I)
COND_CONTRACT = re.compile(r"\$?\d{2,5}(?:\.\d+)?\s?(c|p|calls?|puts?)\b", re.I)
COND_FILL = re.compile(r"(?:^|\s)\$?(\.\d{2}|\d?\.\d{2})\b")

def conditional_plays(msgs, tags):
    """Messages build_plays left as noise that are still a real callout: a strike+side+premium with a
    level condition ('hold only', 'under this call is invalid'). Captured so the record includes them."""
    out = []
    for m in msgs:
        if tags.get(m["id"]) not in ("noise",): continue
        t = m["text"]
        if not COND.search(t) or not COND_CONTRACT.search(t): continue
        sk = bb.strikes(t); tk = bb.tickers(t, m["channel"])
        if not sk: continue
        sw = bb.SIDEW.search(t)
        side = sk[0][1] or ({"call":"call","calls":"call","put":"put","puts":"put"}.get(sw.group(1).lower(),"") if sw else "")
        if side not in ("call","put"): continue
        fm = COND_FILL.search(t)
        fill = fm.group(1) if fm else ""
        if not fill: continue
        out.append(dict(trader=bb.trader_name(m["author"]), channel=m["channel"],
                        ticker=(tk[0] if tk else bb.DEFAULT_TICKER.get(m["channel"],"?")),
                        strike=sk[0][0], side=side, expiry="", fill=fill, msgs=[m], last=m["dt"],
                        standalone=False, closed=False, conditional=True))
    return out

# ---------- verified underlying data ----------
_bars = {}
def bars(sym, day):
    key = (sym, day)
    if key in _bars: return _bars[key]
    p1 = int(dt.datetime.combine(day, dt.time(9, 30), NY).timestamp())
    p2 = int(dt.datetime.combine(day, dt.time(16, 0), NY).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={p1}&period2={p2}&interval=1m"
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        d = json.load(urllib.request.urlopen(r, timeout=25))["chart"]["result"][0]
        ts, q = d["timestamp"], d["indicators"]["quote"][0]
        out = []
        for i, t in enumerate(ts):
            if q["close"][i] is None: continue
            out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).astimezone(NY), q["close"][i], q["high"][i], q["low"][i]))
        _bars[key] = out
    except Exception:
        _bars[key] = []
    return _bars[key]

def verify(play, side_ok):
    """Direction of the UNDERLYING from the call to the session close."""
    t = play["msgs"][0]["dt"].astimezone(NY)
    sym = {"SPX": "^SPX", "SPXW": "^SPX", "NDX": "^NDX", "NDXW": "^NDX", "DJI": "^DJI"}.get(play["ticker"], play["ticker"])
    if sym in ("?", "") or play["side"] not in ("call", "put"): return None
    B = bars(sym, t.date())
    if not B: return None
    at = [b for b in B if b[0] >= t]
    if not at: return None
    p0 = at[0][1]; close = B[-1][1]
    fav = (max(b[2] for b in at) - p0) if play["side"] == "call" else (p0 - min(b[3] for b in at))
    return dict(p0=p0, close=close, chg=(close / p0 - 1) * 100, fav=(fav / p0) * 100,
                correct=(close > p0) if play["side"] == "call" else (close < p0))

def main():
    days = 30; today_only = False
    for i, a in enumerate(sys.argv):
        if a == "--days": days = int(sys.argv[i + 1])
        if a == "--today-only": today_only = True
    moved = merge_inbox()
    msgs, _ = bb.load()
    for m in msgs:
        bb.KNOWN.update(x.upper() for x in bb.DOLLAR_TICK.findall(m["text"]) if x.upper() not in bb.NOT_TICKERS)
        bb.KNOWN.update(bb.re.findall(r"\b([A-Z]{2,5})\s+\$?\d+(?:\.\d+)?\s?(?:c|p|calls?|puts?)\b", m["text"]))
    plays, tags = bb.build_plays(msgs)
    cond = conditional_plays(msgs, tags)
    rows = []
    for p in plays + cond:
        s = bb.score(p)
        instr = p["ticker"] + (f" {p['strike']}{(p['side'][0] if p['side'] in ('call','put') else '')}" if p["strike"] else "")
        rows.append(dict(p, instrument=instr, conditional=p.get("conditional", False), **s))
    out = []
    out.append("## Callout tracking — running record\n")
    if moved: out.append("New messages merged: " + ", ".join(f"{LABEL.get(c,c)} {n}" for c, n in moved) + "\n")
    hdr = "| channel | plays | stated results | stated win rate | stated avg % | underlying calls checked | underlying right | underlying hit rate "
    sep = "|---|---|---|---|---|---|---|---"
    body = []
    tot = dict(plays=0, sc=0, w=0, d=0, rois=[], v=0, vr=0)
    for ch in [c for c in CH_FILE if any(r["channel"] == c for r in rows)]:
        R = [r for r in rows if r["channel"] == ch]
        sc = [r for r in R if r["scored"] and r["roi"] is not None]
        w = sum(1 for r in R if r["outcome"] == "win"); l = sum(1 for r in R if r["outcome"] == "loss"); be = sum(1 for r in R if r["outcome"] == "break-even")
        d = w + l + be; rois = [r["roi"] for r in sc]
        verified = [verify(r, True) for r in R]
        verified = [v for v in verified if v]
        vr = sum(1 for v in verified if v["correct"])
        body.append(f"| {LABEL.get(ch,ch)} | {len(R)} | {len(sc)} | {(f'{w}/{d} = {w/d:.0%}' if d else 'n/a')} | "
                    f"{(f'{sum(rois)/len(rois):+.0f}%' if rois else '—')} | {len(verified)} | {vr} | "
                    f"{(f'{vr}/{len(verified)} = {vr/len(verified):.0%}' if verified else '—')} |")
        tot["plays"] += len(R); tot["sc"] += len(sc); tot["w"] += w; tot["d"] += d; tot["rois"] += rois
        tot["v"] += len(verified); tot["vr"] += vr
    body.append(f"| **all** | {tot['plays']} | {tot['sc']} | {(f'{tot['w']}/{tot['d']} = {tot['w']/tot['d']:.0%}' if tot['d'] else 'n/a')} | "
                f"{(f'{sum(tot['rois'])/len(tot['rois']):+.0f}%' if tot['rois'] else '—')} | {tot['v']} | {tot['vr']} | "
                f"{(f'{tot['vr']}/{tot['v']} = {tot['vr']/tot['v']:.0%}' if tot['v'] else '—')} |")
    out += [hdr, sep] + body
    out.append("")
    out.append("Stated win rate and average % are the trader's own posted numbers (only plays where they stated a result). "
               "Underlying hit rate is independent: for each call with a call/put direction, did the underlying close the session on the right side of where it was when the call posted. "
               "It measures direction, not option P&L — a 0-day contract can be right on direction and still expire worthless.\n")
    cutoff = dt.datetime.now(NY) - dt.timedelta(days=days)
    recent = [r for r in rows if r["msgs"][0]["dt"].astimezone(NY) >= cutoff]
    if today_only:
        tod = dt.datetime.now(NY).date()
        recent = [r for r in recent if r["msgs"][0]["dt"].astimezone(NY).date() == tod]
    if recent:
        out.append("### " + ("Today's callouts" if today_only else f"Callouts, last {days} days") + "\n")
        recent.sort(key=lambda r: r["msgs"][0]["dt"])
        for r in recent[-18:]:
            t = r["msgs"][0]["dt"].astimezone(NY).strftime("%m-%d %H:%M")
            instr = r["instrument"] or r["ticker"]
            fill = f" @{r['fill']}" if r["fill"] else ""
            fill += " (conditional)" if r.get("conditional") else ""
            res = f" → {r['roi']:+.0f}% stated" if r["roi"] is not None else (f" → {r['outcome']}" if r["outcome"] != "unscored" else "")
            v = verify(r, True)
            ver = f" · underlying {v['chg']:+.2f}% by close ({'right' if v['correct'] else 'wrong'})" if v else ""
            out.append(f"- {t} {LABEL.get(r['channel'], r['channel'])}: {instr}{fill}{res}{ver}")
        out.append("")
    txt = "\n".join(out)
    open(os.path.join(BASE, "tracking", "latest.md"), "w").write(txt + "\n")
    print(txt)

if __name__ == "__main__":
    main()
