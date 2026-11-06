# Store builder pre-check — 2026-11-06

The celestial paintings page on bhaeqw-9z is live from Nov 5 and still describes three prints, while the Celestial Paintings collection already includes a fourth Printify poster, Orion, at the same 18×24 matte price of $39.99. This run drafted a four-painting page body and a Dawn layout for that collection in the repo only. Nothing was uploaded, published, priced, or changed on NightLens, and the draft waits for Thomas's yes before it replaces the live page or lands on an unpublished theme.

## What the storefront showed

Read-only. No admin session. Shopify MCP was not authenticated in this environment, so no theme, page, product, or collection write was attempted.

- Shop `bhaeqw-9z`, storefront name Celestial Atlas Prints. Theme id served on the page: `188589113659` (Dawn - Celestial).
- Page [Celestial paintings](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings), published `2026-11-05T09:00:50-05:00`. The body matches the Nov 5 HTML: Moon Phase, Ursa Major, Solar System. Orion is not in it. The rendered sections are the announcement bar, header, the default page body, and the footer. The banner and the painting grid are not on this theme.
- Collection [Celestial Paintings](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings), id `512824901947`, published `2026-11-05T09:00:38-05:00`, updated `2026-11-05T09:24:26-05:00`. Four products, in this order:
  1. Moon Phase `15489780777275`, 18″×24″ matte, $39.99
  2. Ursa Major Constellation Print `15489780810043`, 18″×24″ matte, $39.99
  3. Solar System Chart Print `15489779761467`, 18″×24″ matte, $39.99
  4. Orion Constellation Print `15490090008891`, published `2026-11-05T09:23:30-05:00`, 18″×24″ matte, $39.99, vendor Printify
- Main menu already has "Celestial paintings" pointing at the page. The sticker and the hidden `*-original` drafts are not in this collection.
- `/password` redirects to the storefront. The Nov 4 note that the password was still on is out of date. The trial plan was not rechecked.
- NightLens (`duv5f8-wt`) was not edited.

The Ursa Major product text still says the plate was published in 1824. The page and `SPECS.md` say 1825. That product text was left as it is.

## Prepared in the repo

- `shopify/celestial-prints/pages/celestial-paintings.html` — same three sections, plus Orion (Flamsteed, *Atlas Céleste*, Plate 24, 1776) and a link to the collection, where the four photos already are. Order matches the collection. No new price.
- `shopify/celestial-prints/templates/page.celestial-paintings.json` — Dawn 16.1.1. Banner line "Four unframed charts, printed when you order them." Featured collection shows 4 products in 2 desktop columns. Both numbers are inside Dawn's ranges (`products_to_show` 2–25, `columns_desktop` 1–6). The template check reported the file valid. It was not uploaded.
- `shopify/celestial-prints/celestial-paintings.apply.json` — Nov 5 `"applied": true` record kept. New `pending_revision` `2026-11-06-orion-on-page` with `"applied": false`.
- `shopify/celestial-prints/PAINTINGS.md` and the store README updated so the next run does not recreate the page or treat Orion as unlisted.

The same-day demand note (`morning-reports/precheck-2026-11-06-trending-researcher.md`) did not open the shop, and it still ranks a custom date-and-place star map ahead of these static plates. That map is not on this page. A static poster cannot take a date and a place, and the plate is not drawn. A twelve-sign series is the same kind of later job.

## Not done

- No Shopify mutation. No page body update, no theme upload, no publish, no price change, no collection reorder.
- The live page a buyer opens is still the three-painting text. The four photos are on the collection, not on the page.

## Needs his yes

- Replace the live page body with the four-painting HTML.
- Upload the template onto the unpublished Dawn duplicate only. Do not publish that theme, and do not write the live theme.
- Leave prices, collection order, the sticker, the hidden drafts, and NightLens alone.
- Decide later, as separate jobs, whether a custom date-and-place star map or a zodiac series belongs on this page.
- If he wants the Ursa Major listing to say 1825, that is a product-description edit and was not done here.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-06)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-06)
- [Orion Constellation Print](https://bhaeqw-9z.myshopify.com/products/orion-constellation-print) (read 2026-11-06)
- Dawn 16.1.1 `sections/featured-collection.liquid` and `sections/image-banner.liquid` at tag v16.1.1
- [JSON templates](https://shopify.dev/docs/storefronts/themes/architecture/templates/json-templates)
