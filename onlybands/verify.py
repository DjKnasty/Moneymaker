#!/usr/bin/env python3
"""Recompute Summary from the Plays sheet and assert they match."""
import os, statistics
from openpyxl import load_workbook
wb = load_workbook(os.path.join(os.path.dirname(os.path.abspath(__file__)), "OnlyBands_2month_play_backtest.xlsx"))
P = list(wb["Plays"].iter_rows(values_only=True)); ph = P[0]; plays = [dict(zip(ph, r)) for r in P[1:]]
S = list(wb["Summary"].iter_rows(values_only=True)); sh = S[0]
summ = [dict(zip(sh, r)) for r in S[1:] if r[0] and r[1]]
close = lambda a, b: (a is None and b is None) or (a is not None and b is not None and abs(a - b) < 1e-9)
n = 0
for s in summ:
    R = plays if s["trader"] == "TOTAL" else [p for p in plays if p["channel"] == s["channel"]]
    sc = [p for p in R if p["outcome"] != "unscored"]
    rois = [p["ROI % (trader-stated)"] for p in R if p["ROI % (trader-stated)"] is not None]
    w = sum(p["outcome"] == "win" for p in R); l = sum(p["outcome"] == "loss" for p in R); be = sum(p["outcome"] == "break-even" for p in R)
    d = w + l + be
    checks = {"plays identified": len(R), "plays scored": len(sc), "unscored": len(R) - len(sc), "wins": w, "losses": l, "break-even": be,
              "scored plays with ROI not stated": sum(1 for p in sc if p["ROI % (trader-stated)"] is None)}
    for k, v in checks.items(): assert s[k] == v, (s["trader"], k, s[k], v)
    assert s["win rate (wins / decided scored plays)"] == (f"{w}/{d} = {w/d:.1%}" if d else "n/a (0 decided)"), s["trader"]
    assert close(s["average ROI (plays with stated %)"], sum(rois)/len(rois) if rois else None), s["trader"]
    assert close(s["median ROI"], statistics.median(rois) if rois else None), s["trader"]
    assert close(s["total stated ROI sum"], sum(rois) if rois else 0), s["trader"]
    pos = [p for p in R if (p["ROI % (trader-stated)"] or 0) > 0]; neg = [p for p in R if (p["ROI % (trader-stated)"] or 0) < 0]
    if pos: assert s["best win"].startswith(f"{round(max(p['ROI % (trader-stated)'] for p in pos)*100, 2)}%"), (s["best win"])
    if neg: assert s["worst loss"].startswith(f"{round(min(p['ROI % (trader-stated)'] for p in neg)*100, 2)}%"), (s["worst loss"])
    assert all(p["outcome"] in ("win","loss","break-even") for p in R if p["ROI % (trader-stated)"] is not None)
    n += 1
tot = [s for s in summ if s["trader"] == "TOTAL"][0]
assert tot["plays identified"] == sum(s["plays identified"] for s in summ if s["trader"] != "TOTAL")
print(f"verify OK: {n} summary rows recomputed from {len(plays)} plays")
