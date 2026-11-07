# Store builder pre-check — 2026-11-07

The celestial paintings page on bhaeqw-9z already names four prints, in the order Moon Phase, Ursa Major, Orion, then the solar system, while the Celestial Paintings collection still lists the solar system before Orion. The storefront theme is now Dawn - Vintage Plate Co. Draft (188621029691), and the page still renders only the default page body, so the banner and four-product grid in this repo are not on that theme. Each of the four posters shows a public price of $31.99 with a compare-at of $39.99. This run did not change a price, did not publish a theme or a page, and did not touch NightLens. A revised page body, a collection-order proposal, and an Ursa Major year correction from 1824 to 1825 are in the repo and still need Thomas's yes. Shopify admin was not authenticated here, so nothing was written to an unpublished theme.

## What the storefront showed

Read-only. Shopify MCP needs authentication, and interactive sign-in is not available in this environment, so no theme, page, product, or collection write was attempted.

- Shop `bhaeqw-9z`. Public name Vintage Plate Co. Theme served on the page: `188621029691`, name "Dawn - Vintage Plate Co. Draft", role main, Dawn 16.1.1. Yesterday's note named theme `188589113659` (Dawn - Celestial). That is not the theme the page is serving now.
- Page [Celestial paintings](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings), id `166674628923`, published `2026-11-05T09:00:50-05:00`, updated `2026-11-06T13:07:09-05:00`. The body names four paintings: Moon Phase, Ursa Major, Orion, Solar System. It does not link to the collection, and it does not say that 24×36 is absent. The rendered sections are the announcement bar, header, the default page body, and the footer. `?view=celestial-paintings` renders those same sections, so `templates/page.celestial-paintings.json` is not on this theme.
- Collection [Celestial Paintings](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings), id `512824901947`, four products, updated `2026-11-06T17:24:01-05:00`. Order: Moon Phase, Ursa Major, Solar System, Orion. The description does not list the four titles.
- Each of those four variants is 18″×24″ matte, price $31.99, compare-at $39.99, available. Updated together at `2026-11-07T08:35:56-05:00`. This run did not change them.
- The Ursa Major product text still says the plate was published in 1824. The page, `SPECS.md`, and `sources.json` say 1825.
- Main menu still has "Celestial paintings" pointing at the page. It also has Botanical Plates and National Park Posters. All Prints has 24 products. Those other catalogs were not edited.
- The Solar System sticker is not among the 24 public products. The hidden `*-original` drafts are not in that public list either. Admin was not opened, so draft status was not rechecked.
- `/password` ends on the storefront. The trial plan was not rechecked.
- NightLens (`duv5f8-wt`) was not edited. Its homepage still responds.

The Nov 7 demand note and the Nov 7 supplier note did not open the shop. They still describe the Nov 6 page (three paintings, Orion only in the repo draft) and a poster price of $39.99. This read is later. Those two notes were not rewritten.

## Prepared in the repo

- `shopify/celestial-prints/pages/celestial-paintings.html` — the live four-painting sentences, in the live order, plus a link to the collection and a line that 24 by 36 inches is not on these listings. No price in the copy. This replaces the 2026-11-06 draft, which would have put the solar system ahead of Orion.
- `shopify/celestial-prints/celestial-paintings.apply.json` — `2026-11-06-orion-on-page` is now `superseded_revision` with `"do_not_apply": true`. New `pending_revision` `2026-11-07-page-grid-alignment` with `"applied": false`. It holds the proposed collection order (Orion third, solar system fourth), the description sentence to use only if that reorder is approved, and the Ursa Major paragraph with 1825 instead of 1824.
- `shopify/celestial-prints/templates/page.celestial-paintings.json` — unchanged. Still four products from `celestial-paintings`, two desktop columns, banner line "Four unframed charts, printed when you order them." It must stay off All Prints, which now mixes in the other catalogs.
- `PAINTINGS.md`, the store README, `SPECS.md`, and `STATUS.md` updated so the next run does not paste yesterday's HTML over the live page or treat $39.99 as the price to write back.

## Not done

- No Shopify mutation. No page body update, no theme upload, no publish, no price change, no collection reorder, no product-description edit.
- The live page a buyer opens is still text only. The four photos are on the collection, in a different order from the page.
- An unpublished duplicate of theme `188621029691` was not created. The Nov 5 duplicate `188599370043` was a copy of the older main theme and was not used.

## Needs his yes

- Replace the live page body with `pages/celestial-paintings.html`.
- Reorder the Celestial Paintings collection so it matches the page: Moon Phase, Ursa Major, Orion, Solar System. Only then add the extra description sentence. Leave botanical plates, park posters, the sticker, and the hidden drafts out of that collection.
- Change the Ursa Major description year from 1824 to 1825, using the paragraph in `ursa_year_proposed`. Do not change its price.
- Upload the existing Dawn template onto an unpublished duplicate of theme `188621029691` only. Do not write the live theme, and do not publish that duplicate.
- Leave every price as it is, including the $31.99 / compare-at $39.99 now on the four posters.
- Leave NightLens alone.
- A custom date-and-place star map, and a twelve-sign series, remain separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-07)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-07)
- Public product JSON for the four posters (read 2026-11-07)
- `shopify/celestial-prints/sources.json` (Ursa Major file date 1825)
