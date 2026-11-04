# Job: apply morning-report recommendations to the NasdaqBeast draft page

Owner: Thomas (DjKnasty). Last run: 2026-11-04.
Scope: the NasdaqBeast draft theme `gid://shopify/OnlineStoreTheme/195590717808` on the NightLens store `duv5f8-wt.myshopify.com`. Nothing else.

## What the job does

1. Read the day's morning report in `morning-reports/YYYY-MM-DD.md`.
2. Take only the recommendations it makes for the NasdaqBeast draft page.
3. Apply them to the **unpublished draft theme** via `themeFilesUpsert`. Never the live theme.
4. Record what changed, with before and after for every item, and list anything the report recommends that needs products, photography, or a merchandising decision rather than a theme edit.
5. Push everything to this repo (below).
6. Report step by step. Never publish, send, or make anything live without Thomas's further approval.

## Commit and push rule

All work and commits go into `github.com/DjKnasty/Moneymaker`.

- Every change the bot makes must be committed and pushed to this repo before the job counts as done. That includes the change record in `summaries/`, the applied theme file under `shopify/`, and `STATUS.md`.
- A job run is not complete until each file is actually in the repo on `main` and the commit is confirmed.
- If a push fails, retry it. If it still fails, report the exact failure and treat the job as failed rather than done.
- Always include the commit link or SHA proving the files are in the repo.

This is the same rule the Morning store report routine follows.

## Files this job owns

- `summaries/YYYY-MM-DD-nasdaqbeast-draft-report-implementation.md` — the change record.
- `shopify/nasdaqbeast-draft/templates/index.json` — the homepage JSON as applied, so the repo holds the page itself and re-applying it reproduces the theme state.
- The `Status` line in `STATUS.md` pointing at the newest summary.

## Run log

- 2026-11-04 — Applied the 2026-11-04 morning report (section 2, recs 1, 3 and 6). Reordered Best Sellers and New Arrivals Women, hid the three sample-collection product rows. Theme left unpublished.
