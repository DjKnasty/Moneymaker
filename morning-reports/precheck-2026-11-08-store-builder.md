# Store builder pre-check — 2026-11-08

The celestial paintings page on bhaeqw-9z is still text only, on Dawn - Vintage Plate Co. Draft (188621029691), and it still names Moon Phase, Ursa Major, Orion, then the solar system while the collection lists the solar system before Orion. Every one of the 24 public products is a single 18×24 matte variant at $31.99 with a compare-at of $39.99, but the homepage size strip still offers 12×16 and 24×36, and the National Parks and Botanical tiles still use the solar-system chart and the moon chart while saying those lines are not ready. This run prepared a size strip for the unpublished paintings template, a matching page sentence, product-description drafts, and a homepage edit that must not be pasted over index.json. Shopify admin was not authenticated, so nothing was written to a theme. No price was changed, nothing was published, and NightLens was not touched.

## What the storefront showed

Read-only. Shopify MCP needs authentication, and interactive sign-in is not available in this environment, so no theme, page, product, or collection write was attempted.

- Shop `bhaeqw-9z`. Public name Vintage Plate Co. Theme served on the page: `188621029691`, name "Dawn - Vintage Plate Co. Draft", role main, Dawn 16.1.1. Color schemes on that theme are still the navy, cream, and gold set from the celestial Dawn settings. Scheme-3 is `#06080E`. Scheme-4 is `#F7F1E6`.
- Page [Celestial paintings](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings). The body still matches the Nov 7 reading: four paintings in the order Moon Phase, Ursa Major, Orion, Solar System, no collection link, and a size line that names 18 by 24 inches without saying the other sizes are absent. Rendered sections are the announcement bar, header, the default page body, and the footer. `?view=celestial-paintings` renders those same sections, so `templates/page.celestial-paintings.json` is not on this theme. Dawn writes `template.name` into `data-template`, which stays `page` even when a suffix is set, so this read does not prove the page resource's template suffix was cleared.
- Collection [Celestial Paintings](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings), id `512824901947`, four products. Order: Moon Phase, Ursa Major, Solar System, Orion. The description still does not list the four titles and does not mention size.
- Each of those four variants is 18″×24″ matte, price $31.99, compare-at $39.99, available. They share `updated_at` `2026-11-08T08:38:28-05:00`. This run did not change them. The Ursa Major body still says the plate was published in 1824. The solar-system body names Cellarius, Amsterdam, 1660. This run did not rewrite that sentence.
- The other 20 public products are botanical plates and park or WPA posters. All 24 public variants use the title `18″ x 24″ / Matte` at the same $31.99 / $39.99. The Solar System sticker is not in that list. The hidden `*-original` drafts are not in it either. Admin was not opened, so draft status was not rechecked.
- Homepage size strip, section `template--27812743119163__sizes`: heading "12 × 16 in · 18 × 24 in · 24 × 36 in", text "Most designs ship in 18 × 24 today. Larger and smaller sizes roll out with each new plate." The featured-prints blurb above it already says 18×24 only.
- Homepage tiles, section `template--27812743119163__collections_tiles`: Celestial uses `constellation-ursa-major.jpg` and links to `/collections/celestial-paintings`. National Parks uses `solar-system.jpg`, says "coming soon", and links to All Prints. Botanical uses `moon-phases.jpg`, says "planned next", and links to All Prints. `/collections/vintage-national-parks` and `/collections/vintage-botanical-plates` both returned products.
- Main menu still has "Celestial paintings" pointing at the page, plus Botanical Plates and National Park Posters.
- `/password` returns 302 to the storefront. The trial plan was not rechecked.
- NightLens (`duv5f8-wt`) was not edited. Its homepage still responds with the title Nightlens.

The Nov 7 demand note and the Nov 7 supplier note did not open the shop. They still describe an older page and a poster price of $39.99. This read is later. Those two notes were not rewritten.

## Prepared in the repo

- `shopify/celestial-prints/pages/celestial-paintings.html` — the live four-painting order, plus the collection link, plus a line that neither 12 by 16 nor 24 by 36 is on these listings. No price in the copy.
- `shopify/celestial-prints/templates/page.celestial-paintings.json` — same banner and four-product grid from `celestial-paintings`, two desktop columns, plus a rich-text size section on scheme-4. The grid description now says 18 by 24 inches. Checked against Dawn 16.1.1 section settings for `image-banner`, `featured-collection`, and `rich-text`. Not uploaded.
- `shopify/celestial-prints/theme-draft/homepage-size-and-tiles.proposed.json` — the size-strip replacement and the two tile fixes (park card off the solar-system image and onto `/collections/vintage-national-parks`; botanical card off the moon image and onto `/collections/vintage-botanical-plates`). `"do_not_paste_over": "templates/index.json"`. The celestial tile is left alone until the collection order is approved.
- `shopify/celestial-prints/celestial-paintings.apply.json` — `2026-11-07-page-grid-alignment` stays `pending_revision` with `"applied": false`. New `pending_revision_2026_11_08` id `2026-11-08-size-honesty`, also `"applied": false`. It holds the four proposed product bodies. The Ursa body includes 1825 and the size paragraph, and it supersedes the Nov 7 Ursa paragraph if both are approved. A collection size sentence is separate from the reorder. No price is included as a write.
- `PAINTINGS.md`, the store README, `SPECS.md`, and `STATUS.md` updated so the next run does not treat 12×16 or 24×36 as a size this catalog sells, and does not paste the homepage proposal over `index.json`.

## Not done

- No Shopify mutation. No page body update, no theme upload, no unpublished theme duplicate, no publish, no price change, no collection reorder, no product-description edit, no homepage edit.
- The live page a buyer opens is still text only. The four photos are on the collection, in a different order from the page.
- An unpublished duplicate of theme `188621029691` was not created. The Nov 5 duplicate `188599370043` was a copy of the older main theme and was not used.

## Needs his yes

- Replace the live page body with `pages/celestial-paintings.html`.
- Reorder the Celestial Paintings collection so it matches the page: Moon Phase, Ursa Major, Orion, Solar System. Only then add the four-title description sentence from the Nov 7 proposal. The 18×24-only collection sentence can be approved on its own. Leave botanical plates, park posters, the sticker, and the hidden drafts out of that collection.
- If product descriptions change, apply the Nov 8 bodies once. Do not also paste the Nov 7 Ursa paragraph. Do not change any price. Leave the year at 1824 if he does not want the Ursa sentence changed.
- Upload the Dawn template onto an unpublished duplicate of theme `188621029691` only. Do not write the live theme, and do not publish that duplicate.
- On that same unpublished duplicate, edit the homepage size strip and the National Parks and Botanical tiles from the proposal file. Do not paste that file over `templates/index.json`.
- Leave every price as it is, including the $31.99 / compare-at $39.99 now on all 24 public products.
- Leave NightLens alone.
- A custom date-and-place star map, and a twelve-sign series, remain separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-08)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-08)
- [Vintage Plate Co. homepage](https://bhaeqw-9z.myshopify.com/) (read 2026-11-08)
- Public product JSON for all 24 products (read 2026-11-08)
- `shopify/celestial-prints/sources.json` (Ursa Major file date 1825)
- Dawn 16.1.1 `sections/rich-text.liquid`, `sections/featured-collection.liquid`, and `sections/image-banner.liquid` at tag v16.1.1
