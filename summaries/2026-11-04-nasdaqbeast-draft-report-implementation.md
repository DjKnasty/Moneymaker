# NasdaqBeast draft page — morning report implementation (2026-11-04)

Applied the recommendations from `morning-reports/2026-11-04.md` (section 2, "Product placement") to the **NasdaqBeast - Alphalete layout (draft)** theme (`gid://shopify/OnlineStoreTheme/195590717808`) on the NightLens store (`duv5f8-wt.myshopify.com`).

File changed: `templates/index.json` (theme file, written with `themeFilesUpsert`).
Theme role: **UNPUBLISHED**. Nothing was published, and no product, collection, or live theme was touched.

## What changed

### Rec 1 — Best Sellers row (`nb_best_sellers`)
Scrunch shorts stay in the first two slots; the biker short and crop tee move down.

| Slot | Before | After |
|---|---|---|
| 1 | The Breakout Short | Bull Run Booty Short |
| 2 | Bull Run Booty Short | The Breakout Short |
| 3 | Green Candle Biker Short | Pre-Market Pump Tee |
| 4 | Opening Bell Crop Tee | Blue Chip Training Short |
| 5 | Pre-Market Pump Tee | Green Candle Biker Short |
| 6 | Blue Chip Training Short | Opening Bell Crop Tee |

### Rec 3 — New Arrivals – Women (`nb_new_arrivals_women`)
Leads with the scrunch flare leggings, then the matching set; the half-zip jumpsuit drops to the last slot.

| Slot | Before | After |
|---|---|---|
| 1 | Market Open Half-Zip Jumpsuit | Bull Flag Scrunch Flare Leggings |
| 2 | After Hours Backless Flare Jumpsuit | Bid & Ask Tee + Scrunch Short Set |
| 3 | Bid & Ask Tee + Scrunch Short Set | After Hours Backless Flare Jumpsuit |
| 4 | Bull Flag Scrunch Flare Leggings | Market Open Half-Zip Jumpsuit |

### Rec 6 — Theme housekeeping
The three built-in `product-list` sections were still pointing at `electronics-and-accessories-example-products` (4 sample items). Since the store has no clothing products yet, they are now hidden rather than showing sample rows:

- `new_arrivals_women` — hidden
- `new_arrivals_men` — hidden
- `best_sellers` — hidden

Set `"disabled": true` on each. The collection reference was left in place, so re-enabling them (or repointing them at real collections) is a one-line change once products exist.

## Not applied — recommended, needs decisions or assets

These are from the same report but cannot be implemented in a theme file:

- **Rec 2 — seamless sports bra / halter bra.** Needs a supplier product and photography; the draft has no bra at all.
- **Rec 4 — men's cutoff tank and tapered jogger or cargo pant.** Needs products.
- **Rec 5 — one trend color for the first drop** (dusty rose, sage, or a red). A merchandising decision plus new product colorways; the page palette is unchanged.
- **Rec 6 follow-up — point the three rows at real collections.** Blocked until clothing products exist; hiding them is the interim fix the report allows.
- **Section 3, image tidy.** All flagged swaps (Leggings & Shorts tile sneakers with smeared side panels, hero and lifestyle banners under 2400 px wide, half-zip jumpsuit flat studio shot, community post 4) need replacement photography. Alt text is already generated from each block's title by the section templates, so the "rewrite alt text" item lands with the real product photos.

## Verification

- Theme file `templates/index.json` size 23,496 bytes; theme `updatedAt` 2026-11-04T18:42:43Z.
- Theme role confirmed `UNPUBLISHED` after the write.

## Repo files

- `summaries/2026-11-04-nasdaqbeast-draft-report-implementation.md` — this record.
- `shopify/nasdaqbeast-draft/templates/index.json` — the exact homepage JSON written to the draft theme, so the repo holds the page as applied. Re-applying it reproduces the theme state above.
- `jobs/nasdaqbeast-draft-report.md` — the job spec, stating that all work and commits go into this repo and that a failed push is a failed job, not a finished one.
- `STATUS.md` — latest summary pointer.

All are committed and pushed to `main` in `DjKnasty/Moneymaker`.

## Commits

- `80d5ee2` — change record
- `5fefdf4` — applied homepage JSON
- `fd77c1f` — record updated with the repo file list
- `fca4635` — STATUS.md pointer
- `22adc11` — job spec with the mandatory commit-and-push rule
