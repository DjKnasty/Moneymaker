#!/usr/bin/env python3
"""OnlyBands play backtest. Re-run: python3 /workspace/onlybands/build_backtest.py
Globs raw/*.jsonl, dedupes by message id, rule-based play extraction. No prices are looked up or modeled."""
import json, glob, re, statistics, os, hashlib
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from zoneinfo import ZoneInfo
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "OnlyBands_2month_play_backtest.xlsx")
NY = ZoneInfo("America/New_York")
GAP = timedelta(hours=24)        # play closes after 24h with no attached message
LATE = timedelta(hours=2)        # untagged result within 2h of a closed play re-attaches to it
CHANNEL_FROM_FILE = {"qqq-hipp.jsonl": "odte-qqq-hipp-trades", "qqq-hipp-early.jsonl": "odte-qqq-hipp-trades", "iwm-jaycee.jsonl": "odte-iwm-jaycee-trades", "teej-breakout.jsonl": "teej-breakout-trades", "bucky-budget.jsonl": "bucky-budget-swings"}
DEFAULT_TICKER = {"odte-qqq-hipp-trades": "QQQ", "odte-iwm-jaycee-trades": "IWM"}

def trader_name(a):
    return (a or "(unknown author)").split("|")[0].strip()

# ---------- regexes ----------
NOT_TICKERS = {"EVERYONE","PT","TP","DTE","ODTE","AM","PM","ITM","OTM","AI","CEO","FOMC","CPI","USA","OK","LOL","HIGH","LOW","STOP","IN","OUT","THE","AND","FOR","ALL","ATH","EOD","PDT","ETF","EPS","Q3","Q4","II","IV","UP","SO","OR","IF","ON","AT","OF","TO","ME","MY","IT","IS","GO","NO","BE","WE","RN","HOD","LOD","PLAY","CALL","PUT","CALLS","PUTS","TRADE","LEAPS","FILL","SOLD","HALF","GAP","BULLISH","BEARISH","OPTIONS","SWING","JANUARY","TRADES","NOTHING","ELSE","NONE","OTHER","TARGET","HIT","GAMEPLAN","LOTTO","DONE","GUYS","RECAP","EARNINGS","THE","NUMBERS","STOPS","MANAGEMENT","UPDATE","W","I","A"}
DOLLAR_TICK = re.compile(r"\$([A-Za-z]{1,5})\b")
BARE_TICK = re.compile(r"\b([A-Z]{2,5})\b")
STRIKE = re.compile(r"\$?(\d{2,5}(?:\.\d+)?)\s?(?:'?s\b|’s\b|(c|p|calls?|puts?)\b)", re.I)
SIDEW = re.compile(r"\b(calls?|puts?|shares?)\b", re.I)
EXPIRY = re.compile(r"\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b|\b(0\s?day|0\s?dte|\d+\s?-?\s?\d*\s?dte)\b|\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})", re.I)
FILL = re.compile(r"(?:\bat|@)\s*\$?(\d*\.\d+)|\$?(\d*\.\d+)\s*fill|(?<![\d$.])(\.\d{2})\b", re.I)
ENTRY = re.compile(r"(?:^|[.!\n]\s*|@everyone\s+)(?:back\s+|got\s+back\s+)?in\s+(?:\$|[A-Za-z]{2,5}\b|a\b|lotto|high|super)|\b(?:i'?m in|im in|only thing i'?m in|entered|entering|bought|buying|added|adding|grabbed|taking \$|trying \$|took \$|starter position|reload(?:ed|ing)?|back in|same play)\b|\d*\.\d+\s*(?:fills?|fil)\b|\bfill\s*(?:at|@)?\s*\$?\d*\.\d+|for the \$?\d+k account|in the \$?\d+k account|\d+ shares (?:of )?\$?[A-Z]|selling \$?\d+.*call to collect", re.I)
NONENTRY = re.compile(r"\b(watching|watchlist|watch list|gameplan|i like (?:calls|puts)|if price|(?:options|leaps|swing) call|alert|announcement|spots|academy)\b", re.I)
EXIT = re.compile(r"\b(sold|selling|sell|out of|i'?m out|out guys|closed|closing|cashed|took profit|taking profit|take profit|targets? (?:🎯 )?hit|pt hit|tp hit|stopped(?: out)?|stop (?:loss )?(?:got )?(?:hit|triggered)|stops? triggered|got stop|(?:closed|out|went|exited) flat|break ?even\b(?! stop)|done for the day)\b|^\s*out\b", re.I)
NOT_EXIT = re.compile(r"thought my|still in\b|\b(raise|raising|set|move|moving)\b[^.]*\b(stops?|break ?even)\b|stops? (?:at|to) break ?even|selling (?:calls|options|premium)|\bto collect\b", re.I)
BARE_ENTRY = re.compile(r"^\W*(?:\d{1,2}/\d{1,2}(?:/\d{2,4})?\s+)?\$?[A-Z]{1,5}\s+(?:\d{1,2}/\d{1,2}(?:/\d{2,4})?\s+)?\$?\d+(?:\.\d+)?\s?(?:c|p|calls?|puts?)\b[^\n]{0,15}?\$?\d*\.\d+", re.M)
TARGETW = re.compile(r"(target(?:ing)?|price target|\bPT\b|\bTP\b)[^\n]{0,80}", re.I)
STOPW = re.compile(r"(stop(?: loss)?[^\n]{0,70})", re.I)
PCT = re.compile(r"(?<![\w.$])([+-]?\d{1,4}(?:\.\d+)?)\s?%")
PCT_BAD_BEFORE = re.compile(r"(risk(?:ing)?|over|under|get|set at|max|tp at|take profit at|stop(?: loss)?(?: is| at)?|discount|sold|selling|sell|down|expect\w*|roughly|move|beat|of)\s*$", re.I)
PCT_BAD_AFTER = re.compile(r"^\s*(for the rest|max|stop|discount|move|of\b|position|in premium|on a|account|off|in either)", re.I)
LOSSW = re.compile(r"\b(for a loss|took a loss|small loss|loss)\b", re.I)
BEW = re.compile(r"\b(break ?even|(?:closed|out|went|exited) flat)\b", re.I)
TGTHIT = re.compile(r"\b(targets? (?:🎯 )?hit|pt hit|tp hit)\b", re.I)

KNOWN = set()   # filled in main(): every $TICKER seen anywhere in the corpus
CI_TICKERS = {"IWM","SPY","SPX","QQQ","NVDA","TSLA","SPCX","ASTS","AMZN","PLTR","RDDT","INTC","HOOD","GOOGL","RIVN","SOFI","AAPL","META","MSFT","AMD"}
NAMES = {"amazon": "AMZN", "tesla": "TSLA", "nvidia": "NVDA", "google": "GOOGL", "apple": "AAPL", "palantir": "PLTR", "reddit": "RDDT", "intel": "INTC"}
def tickers(text, channel):
    found = []
    for m in DOLLAR_TICK.finditer(text):
        x = m.group(1).upper()
        if x not in NOT_TICKERS: found.append((m.start(), x))
    for m in re.finditer(r"\b([A-Za-z]{1,8})\b", text):
        w = m.group(1); u = w.upper()
        if u in NOT_TICKERS: continue
        if (u in CI_TICKERS) or (w.isupper() and len(w) >= 2 and u in KNOWN): found.append((m.start(), u))
        elif w.lower() in NAMES: found.append((m.start(), NAMES[w.lower()]))
    out = []
    for _, x in sorted(found):
        if x not in out: out.append(x)
    return out

def strikes(text):
    res = []
    for m in STRIKE.finditer(text):
        v = m.group(1); suf = (m.group(2) or "").lower()
        if "." in v and float(v) < 10: continue
        side = "call" if suf.startswith("c") else "put" if suf.startswith("p") else ""
        res.append((v, side))
    return res

def stated_pcts(text):
    vals = []
    for m in PCT.finditer(text):
        if PCT_BAD_BEFORE.search(text[:m.start()]) or PCT_BAD_AFTER.search(text[m.end():]):
            continue
        v = float(m.group(1))
        if re.search(r"\bdown\s*$", text[:m.start()], re.I): v = -abs(v)
        vals.append(v)
    return vals

def is_entry(text):
    if NONENTRY.search(text) and not re.search(r"\d*\.\d+\s*fill|\bin \$|^\s*in\b", text, re.I): return False
    if not ENTRY.search(text) and not BARE_ENTRY.search(text): return False
    has_instr = bool(strikes(text)) or bool(re.search(r"shares|\$[A-Za-z]{1,5}|calls?|puts?|\d+\s?[cp]\b|fill", text, re.I))
    return has_instr

def pcts_for(text, ticker):
    """If a message names several tickers, keep only the % segment that belongs to this play's ticker."""
    tks = tickers(text, "")
    if len(tks) > 1 and ticker in tks:
        parts = re.split(r"(?=\$?\b(?:%s)\b)" % "|".join(map(re.escape, tks)), text, flags=re.I)
        seg = [x for x in parts if tickers(x, "")[:1] == [ticker]]
        return [v for x in seg for v in stated_pcts(x)]
    return stated_pcts(text)

def is_exit(text):
    if re.search(r"riders|runners", text, re.I) and not re.search(r"\b(sold|selling|sell|stopped|closed)\b", text, re.I): return False
    return bool(EXIT.search(text)) and not (NOT_EXIT.search(text) and not re.search(r"\b(sold|out|closed|stopped|hit)\b", text, re.I))

# ---------- load ----------
def load():
    msgs = {}
    files = sorted(glob.glob(os.path.join(BASE, "raw", "*.jsonl")))
    for f in files:
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line: continue
            try: m = json.loads(line)
            except Exception: continue
            m.setdefault("channel", CHANNEL_FROM_FILE.get(os.path.basename(f), os.path.basename(f)[:-6]))
            if not m.get("id"):  # Jaycee/Teej files have no id: synthesize a stable one from content
                m["id"] = "syn-" + hashlib.sha1((m["channel"] + m["ts"] + m.get("author", "") + (m.get("text") or "")).encode()).hexdigest()[:16]
            msgs.setdefault(m["id"], m)
    for m in msgs.values():
        m["dt"] = datetime.fromisoformat(m["ts"].replace("Z", "+00:00"))
        m["trader"] = trader_name(m["author"])
        m["text"] = m.get("text") or ""
    return sorted(msgs.values(), key=lambda m: m["dt"]), files

# ---------- play extraction ----------
def build_plays(msgs):
    plays = []; tags = {}
    by_ch = defaultdict(list)
    for m in msgs: by_ch[m["channel"]].append(m)
    for ch, L in by_ch.items():
        openp = []; closed = []
        primary = Counter(m["trader"] for m in L).most_common(1)[0][0]
        for m in L:
            if m["trader"] != primary: tags[m["id"]] = "other-author"; continue
            t = m["text"]; now = m["dt"]
            for p in list(openp):
                if now - p["last"] > GAP: openp.remove(p); closed.append(p)
            tk = tickers(t, ch); sk = strikes(t)
            ent, ex, pc = is_entry(t), is_exit(t), stated_pcts(t)
            def match(pool):
                for p in reversed(pool):
                    if tk and p["ticker"] not in tk: continue
                    if sk and p["strike"] and p["strike"] not in [s for s, _ in sk]:
                        if tk or ch in DEFAULT_TICKER: continue
                    return p
                return None
            if ent:
                norm = lambda x: re.sub(r"\s+", " ", re.sub(r"\(edited\).*", "", x)).strip().lower()
                dup = next((p for p in openp + [c for c in closed if now - c["last"] <= timedelta(hours=48)] if norm(p["msgs"][0]["text"]) == norm(t)), None)
                if dup: dup["msgs"].append(m); dup["last"] = now; tags[m["id"]] = "repost"; continue
                if not tk and not sk and openp and not re.search(r"back in|same play", t, re.I):
                    p = openp[-1]; p["msgs"].append(m); p["last"] = now; tags[m["id"]] = "continuation"
                    if not p["fill"]:
                        fm = FILL.search(t); p["fill"] = next((g for g in fm.groups() if g), "") if fm else ""
                    continue
                tick = tk[0] if tk else (DEFAULT_TICKER.get(ch) or (openp[-1]["ticker"] if openp else "?"))
                s = sk[0] if sk else ("", "")
                sw = SIDEW.search(t)
                side = s[1] or ({"call":"call","calls":"call","put":"put","puts":"put","share":"share","shares":"share"}.get(sw.group(1).lower(), "") if sw else "")
                if re.search(r"selling \$?\d+.*call", t, re.I): side = "sold call"
                if not s[0] and not tk and openp and re.search(r"back in|same plan|same play", t, re.I):
                    # re-entry into same contract: continues as a NEW play on prior instrument
                    prev = openp[-1]; tick = prev["ticker"]; s = (prev["strike"], prev["side"]); side = prev["side"]
                fm = FILL.search(t)
                fill = next((g for g in fm.groups() if g), "") if fm else ""
                ex_m = EXPIRY.search(t)
                p = dict(trader=m["trader"], channel=ch, ticker=tick, strike=s[0], side=side or "unclear",
                         expiry=(next(g for g in ex_m.groups() if g) if ex_m else ""), fill=fill,
                         msgs=[m], last=now, standalone=False, closed=False)
                # an entry on a new contract closes nothing else (traders run multiple legs)
                openp.append(p); plays.append(p); tags[m["id"]] = "entry"
                if ex and pc: p["closed"] = False
                continue
            relevant = ex or pc or tk or sk or TARGETW.search(t) or STOPW.search(t)
            if not relevant: tags[m["id"]] = "noise"; continue
            target = match(openp)
            if target is None and (ex or pc):
                recent = [p for p in closed if now - p["last"] <= LATE]
                target = match(recent)
                if target: closed.remove(target); openp.append(target)
            if target is None and ex and tk:
                # swing continuation: exit naming the ticker of a still-unexited play opened <=14 days earlier
                cands = [p for p in closed if not p["standalone"] and p["ticker"] in tk and now - p["msgs"][0]["dt"] <= timedelta(days=14)
                         and not any(is_exit(x["text"]) for x in p["msgs"][1:])]
                target = cands[-1] if cands else None
                if target: closed.remove(target); openp.append(target)
            if target is not None:
                target["msgs"].append(m); target["last"] = now; tags[m["id"]] = "continuation"
                if ex and re.search(r"\b(out of everything|i'?m out|out guys|closed|stopped out|done for the day|all targets hit)\b|^\s*out\b", t, re.I) \
                        and not re.search(r"minus runners|still riding|riders", t, re.I):
                    openp.remove(target); closed.append(target)
                continue
            if ex and pc and (tk or sk) and not NONENTRY.search(t):
                # single message that both names an instrument and states a result (entry not in data)
                tick = tk[0] if tk else DEFAULT_TICKER.get(ch, "?")
                s = sk[0] if sk else ("", "")
                p = dict(trader=m["trader"], channel=ch, ticker=tick, strike=s[0], side=s[1] or "unclear",
                         expiry="", fill="", msgs=[m], last=now, standalone=True)
                plays.append(p); closed.append(p); tags[m["id"]] = "standalone-result"; continue
            tags[m["id"]] = "noise"
    return plays, tags

def score(p):
    exits = [m for m in p["msgs"][1:] if is_exit(m["text"])]
    if p["standalone"]: exits = [p["msgs"][0]] + exits
    if not p["standalone"] and is_exit(p["msgs"][0]["text"]) and stated_pcts(p["msgs"][0]["text"]):
        exits = [p["msgs"][0]] + exits
    texts = [m["text"] for m in exits]
    vals = [v for t in texts for v in pcts_for(t, p["ticker"])]
    allt = " ".join(m["text"] for m in p["msgs"])
    tg = "; ".join(dict.fromkeys(x.group(0).strip() for m in p["msgs"] for x in TARGETW.finditer(m["text"])))[:300]
    st = "; ".join(dict.fromkeys(x.group(0).strip() for m in p["msgs"] for x in STOPW.finditer(m["text"])))[:300]
    r = dict(targets=tg, stops=st, result_text=" || ".join(t.replace("\n", " ") for t in texts)[:1500],
             exit_ts=exits[-1]["dt"] if exits else None, roi=None, basis="not stated", outcome="unscored", conf="low", scored=False)
    if not exits: return r
    r["scored"] = True
    if vals:
        r["roi"] = round(sum(vals) / len(vals), 2)
        r["basis"] = "stated" if len(vals) == 1 else "partial-weighted (simple avg of trader-stated partials)"
        r["conf"] = "high"
        r["outcome"] = "win" if r["roi"] > 0 else "loss" if r["roi"] < 0 else "break-even"
        return r
    r["conf"] = "medium"; jt = " ".join(texts)
    if LOSSW.search(jt): r["outcome"] = "loss"
    elif BEW.search(jt): r["outcome"] = "break-even"
    elif TGTHIT.search(jt): r["outcome"] = "win"
    else: r["outcome"] = "exit, result not stated"
    return r

def fmt(dt): return dt.astimezone(NY).strftime("%Y-%m-%d %H:%M") if dt else ""

def stats(rows):
    sc = [r for r in rows if r["scored"]]
    w = sum(r["outcome"] == "win" for r in rows); l = sum(r["outcome"] == "loss" for r in rows); be = sum(r["outcome"] == "break-even" for r in rows)
    rois = [r["roi"] for r in rows if r["roi"] is not None]
    best = max((r for r in rows if r["roi"] is not None and r["roi"] > 0), key=lambda r: r["roi"], default=None)
    worst = min((r for r in rows if r["roi"] is not None and r["roi"] < 0), key=lambda r: r["roi"], default=None)
    d = w + l + be
    return dict(plays=len(rows), scored=len(sc), unscored=len(rows) - len(sc), wins=w, losses=l, be=be,
                winrate=(f"{w}/{d} = {w/d:.1%}" if d else "n/a (0 decided)"),
                avg=(sum(rois)/len(rois)/100 if rois else None), med=(statistics.median(rois)/100 if rois else None),
                best=(f"{best['roi']}% {best['instrument']} {best['entry_ts'][:10]}" if best else "none stated"),
                worst=(f"{worst['roi']}% {worst['instrument']} {worst['entry_ts'][:10]}" if worst else "none stated"),
                total=(sum(rois)/100 if rois else 0), notstated=sum(1 for r in sc if r["roi"] is None))

SUMCOLS = ["trader","channel","date range covered (ET)","window note","total messages read","plays identified","plays scored","unscored",
           "wins","losses","break-even","win rate (wins / decided scored plays)","average ROI (plays with stated %)","median ROI","best win","worst loss","total stated ROI sum","scored plays with ROI not stated"]

def main():
    msgs, files = load()
    for m in msgs:
        KNOWN.update(re.findall(r"\b([A-Z]{2,5})\s+\$?\d+(?:\.\d+)?\s?(?:c|p|calls?|puts?)\b", m["text"]))
        KNOWN.update(re.findall(r"\d{1,2}/\d{1,2}(?:/\d{2,4})?\s+([A-Z]{2,5})\s+\$?\d", m["text"]))
        KNOWN.difference_update(NOT_TICKERS)
        KNOWN.update(x.upper() for x in DOLLAR_TICK.findall(m["text"]) if x.upper() not in NOT_TICKERS)
    plays, tags = build_plays(msgs)
    rows = []
    cnt = Counter()
    for p in plays:
        cnt[p["trader"]] += 1
        s = score(p)
        instr = p["ticker"] + (f" {p['strike']}{(p['side'][0] if p['side'] in ('call','put') else '')}" if p["strike"] else "")
        rows.append(dict(trader=p["trader"], channel=p["channel"], play_id=f"{p['trader'][:5].upper()}-{cnt[p['trader']]:03d}",
            entry_ts=fmt(p["msgs"][0]["dt"]) + (" (entry not in data; result msg)" if p["standalone"] else ""), instrument=instr,
            side=p["side"], strike=p["strike"], expiry=p["expiry"], fill=p["fill"], ids=" ".join(m["id"] for m in p["msgs"]),
            entry_text=p["msgs"][0]["text"].replace("\n", " ")[:400], month=p["msgs"][0]["dt"].astimezone(NY).strftime("%Y-%m"), **s))
    by_ch = defaultdict(list)
    for m in msgs: by_ch[m["channel"]].append(m)
    wb = Workbook(); B = Font(bold=True)
    def sheet(ws, header, data, widths=None, pctcols=()):
        ws.append(header)
        for c in ws[1]: c.font = B; c.alignment = Alignment(wrap_text=True, vertical="top")
        for r in data: ws.append(r)
        ws.freeze_panes = "A2"
        for i, h in enumerate(header, 1):
            ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(h, min(45, max(12, len(str(h)) + 2)))
        for h in pctcols:
            ci = header.index(h) + 1
            for row in ws.iter_rows(min_row=2, min_col=ci, max_col=ci):
                for c in row:
                    if isinstance(c.value, (int, float)): c.number_format = "0.0%"
    # Summary
    ws = wb.active; ws.title = "Summary"
    srows = []; traders = []
    for ch, L in by_ch.items():
        tr = Counter(m["trader"] for m in L).most_common(1)[0][0]; traders.append((tr, ch, L))
    for tr, ch, L in traders + [("TOTAL", "all", msgs)]:
        R = rows if tr == "TOTAL" else [r for r in rows if r["channel"] == ch]
        st = stats(R)
        a, b = L[0]["dt"].astimezone(NY), L[-1]["dt"].astimezone(NY)
        span = (b.date() - a.date()).days + 1
        note = "" if tr == "TOTAL" else (f"{span} calendar days: meets ~2-month window" if span >= 58 else f"ONLY {span} calendar days of history - does NOT cover 2 months")
        srows.append([tr, ch, f"{a:%Y-%m-%d} to {b:%Y-%m-%d}", note, len(L), st["plays"], st["scored"], st["unscored"], st["wins"], st["losses"], st["be"],
                      st["winrate"], st["avg"], st["med"], st["best"], st["worst"], st["total"], st["notstated"]])
    sheet(ws, SUMCOLS, srows, {"window note": 40, "best win": 30, "worst loss": 30, "win rate (wins / decided scored plays)": 22, "channel": 26},
          ("average ROI (plays with stated %)", "median ROI", "total stated ROI sum"))
    ws.append([]); ws.append(["NOTE: Win rate = wins / (wins+losses+break-even) among scored plays only; denominator shown. "
        "ROI = trader-stated percent on exit/sell/target/stop messages (simple average if several partials were stated); never modeled or looked up. "
        "Average/median/sum use only plays with a stated %. Scored plays with exit language but no number ('out', 'sold a bunch') have blank ROI and are excluded from win rate unless they say loss/break-even/target hit. "
        "Running marks like '60% here' are NOT treated as results. Total ROI sum is a sum of per-play percents, not a portfolio return."])
    ws.cell(ws.max_row, 1).alignment = Alignment(wrap_text=True); ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=12)
    ws.row_dimensions[ws.max_row].height = 90
    # Plays
    PH = ["trader","channel","play id","entry timestamp (ET)","instrument","side","strike","expiry","entry/fill","entry message text","targets","stops",
          "exit/result timestamp (ET)","stated result text (verbatim)","ROI % (trader-stated)","ROI basis","outcome","confidence","message ids consumed"]
    sheet(wb.create_sheet("Plays"), PH, [[r["trader"], r["channel"], r["play_id"], r["entry_ts"], r["instrument"], r["side"], r["strike"], r["expiry"], r["fill"],
        r["entry_text"], r["targets"], r["stops"], fmt(r["exit_ts"]), r["result_text"], (r["roi"]/100 if r["roi"] is not None else None), r["basis"], r["outcome"], r["conf"], r["ids"]] for r in rows],
        {"entry message text": 50, "stated result text (verbatim)": 60, "targets": 30, "stops": 30, "message ids consumed": 40, "ROI basis": 22}, ("ROI % (trader-stated)",))
    # By month
    MH = ["trader","month","messages","plays","scored","unscored","wins","losses","break-even","win rate","average ROI","median ROI","total stated ROI sum","scored, ROI not stated"]
    md = []
    for tr, ch, L in traders:
        for mo in sorted({m["dt"].astimezone(NY).strftime("%Y-%m") for m in L}):
            R = [r for r in rows if r["channel"] == ch and r["month"] == mo]; st = stats(R)
            md.append([tr, mo, sum(1 for m in L if m["dt"].astimezone(NY).strftime("%Y-%m") == mo), st["plays"], st["scored"], st["unscored"], st["wins"], st["losses"], st["be"], st["winrate"], st["avg"], st["med"], st["total"], st["notstated"]])
    sheet(wb.create_sheet("By month"), MH, md, {"win rate": 20}, ("average ROI", "median ROI", "total stated ROI sum"))
    # Method
    tc = Counter(tags.values()); n = len(msgs)
    method = [
        ("Data", f"Files globbed: {', '.join(os.path.basename(f) for f in files)}. {n} unique messages after de-duping by message id. Raw files are read-only inputs; nothing was looked up externally."),
        ("Classification", f"entry={tc['entry']}, continuation={tc['continuation']}, repost of an open entry={tc['repost']}, standalone result message={tc['standalone-result']}, noise={tc['noise']}, other-author messages (excluded)={tc['other-author']}. Play-related = {(n-tc['noise']-tc['other-author'])/n:.1%} of messages; noise = {tc['noise']/n:.1%}."),
        ("Play-grouping rule", "A play starts at an entry message: entry verb (in / back in / entered / bought / added / starter position / reloaded) or the word 'fill' or 'for/in the $1k account' or 'N shares of X' or an opening covered-call sale, AND an instrument token (ticker, strike like $715 / 280C / $704s, calls/puts/shares). Setups, watchlists, 'gameplan', 'I like calls if...', 'alert' and Teej's 'BULLISH OPTIONS CALL' trigger write-ups without a fill are NOT plays. "
            "Later messages attach to the most recent open play whose ticker (and strike, if one is mentioned) matches; messages with no ticker attach to the most recent open play. A play closes on 'out / I'm out / out of everything / closed / stopped out / done for the day' (unless it says runners/still riding), or after 24h with no attached message. A result message within 2h after a close re-attaches to that play (handles 'out... apologies, still in'). A new entry on a different strike/ticker is a new play; multiple plays can be open at once. An exact repost of an open play's entry text is absorbed into it. A message that names an instrument and states a result with no open play becomes a one-message play with the entry marked 'not in data'."),
        ("Outcome rules", "Only messages with exit language (sold/selling/out/closed/cashed/took profit/target hit/PT hit/stopped/stop hit/flat/break even) inside a play count as results. Percentages in those messages are the stated ROI; several are simple-averaged and labelled partial-weighted. Percents for risk, max stop, TP-at, discounts, expected moves, or position size ('sold 50%') are excluded. "
            "Running marks ('60% here', '+35%') with no exit language are NOT results. Exit with no number: 'loss' -> loss, 'break even/flat' -> break-even, 'target hit' -> win (medium confidence), otherwise 'exit, result not stated' (scored but excluded from win rate, ROI blank). No exit language -> unscored, ROI blank. Confidence: high = % stated, medium = exit language only, low = unscored. No underlying-move ROI was computed because exits rarely give an underlying exit price; basis 'underlying-move' is therefore unused."),
        ("Judgement calls", "1) Biggest: running unrealized marks are not counted as results even when the trader clearly profited, which leaves many Hipp/Jaycee plays as 'exit, result not stated' or unscored and drops their headline ROI coverage. 2) 'Selling a bunch' with a % in the same message counts as a stated partial; a % posted one message before 'selling a bunch' is not borrowed. 3) Jaycee posts multi-leg marks like '66 75 40%'; only %-suffixed numbers are read (so '40%'). 4) 'Target hit ... still riding' counts as a stated partial result. 5) Teej covered-call / premium-collection and LEAPS posts are counted as plays when they state a position; they mostly have no stated result. 6) Conditional alerts without 'in'/'fill' (e.g. Jaycee '$TSLA under X only ... $350p .80') are not plays. 7) Reposted identical entries are one play. 8) Only each channel's most frequent author is treated as the trader; messages from other authors and messages with a null author field (20 in the Hipp file, some clearly from a stand-in poster) are excluded from plays but counted as messages read. 9) An exit naming a ticker of an un-exited play opened up to 14 days earlier re-attaches to it (swing exits)."),
        ("Limitations", "Regex/heuristic classification, not hand-labelled: some entries/exits will be mis-tagged; spot-check via message ids. Traders choose what to report: losses are under-posted relative to wins (survivorship of stated results). Simple average of partials ignores position sizing. Stated percents are option-premium moves on unknown size and cannot be summed into account returns. Fills are as posted (often only premium). Edited messages are taken in their final form. Teej's channel only starts 2026-10-28 (about one week) and cannot supply two months; Hipp's main file starts 2026-09-15 unless the qqq-hipp-early file is present. Bucky's file was absent at build time unless listed under Data; re-run to include it."),
    ]
    sheet(wb.create_sheet("Method"), ["topic", "description"], method, {"topic": 20, "description": 150})
    for row in wb["Method"].iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    # Raw counts
    ws = wb.create_sheet("Raw counts")
    ws.append(["COVERAGE"]); ws["A1"].font = B
    ws.append(["channel","trader","first message (ET)","last message (ET)","calendar days","messages","meets 2-month window?"])
    for c in ws[2]: c.font = B
    for tr, ch, L in traders:
        a, b = L[0]["dt"].astimezone(NY), L[-1]["dt"].astimezone(NY); sp = (b.date() - a.date()).days + 1
        ws.append([ch, tr, f"{a:%Y-%m-%d %H:%M}", f"{b:%Y-%m-%d %H:%M}", sp, len(L), "yes" if sp >= 58 else "NO"])
    ws.append([]); ws.append(["MESSAGES PER CHANNEL PER DAY (ET)"]); ws.cell(ws.max_row, 1).font = B
    ws.append(["date","channel","messages","play-language messages (entry/exit/% words)","messages tagged into plays"])
    for c in ws[ws.max_row]: c.font = B
    pl = re.compile(r"%|\bfill\b|\bsold\b|\bstop|\btarget|\bin \$|\bcalls?\b|\bputs?\b", re.I)
    d = defaultdict(lambda: [0, 0, 0])
    for m in msgs:
        k = (m["dt"].astimezone(NY).strftime("%Y-%m-%d"), m["channel"])
        d[k][0] += 1; d[k][1] += bool(pl.search(m["text"])); d[k][2] += tags.get(m["id"]) not in ("noise", "other-author")
    for k in sorted(d): ws.append([k[0], k[1], *d[k]])
    ws.freeze_panes = "A3"
    for i, w in enumerate([24, 26, 20, 20, 30, 12, 20], 1): ws.column_dimensions[get_column_letter(i)].width = w
    wb.save(OUT)
    print("wrote", OUT, "|", n, "messages |", len(rows), "plays |", dict(tc))

if __name__ == "__main__":
    main()
