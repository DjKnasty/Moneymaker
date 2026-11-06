# Celestial paintings page

Print-on-demand store `bhaeqw-9z.myshopify.com` only. The telescope shop was not edited. Nothing on this page is held in inventory. Printify prints each order.

## 2026-11-06 draft (not sent to Shopify)

A read of the public storefront found the page and the collection already live from Nov 5, and found a gap between them. The page body still names three paintings. The collection `celestial-paintings` (id `512824901947`) has four Printify posters, in this order: Moon Phase, Ursa Major, Solar System, Orion. Orion (`orion-constellation-print`, product id `15490090008891`) was published 2026-11-05 at 09:23, about twenty minutes after the page. It is 18×24 matte at the same $39.99 already on the other three. This run did not change that price.

The live page is the default page section on theme `188589113659` (Dawn - Celestial, the theme the storefront is serving). It does not render the banner or the painting grid. The alternate template is still only a file in this repo, meant for the unpublished Dawn duplicate, and it was not uploaded today.

The repo draft now matches the four paintings that are already for sale:

- `pages/celestial-paintings.html` adds Orion (Flamsteed, *Atlas Céleste*, Plate 24, 1776) and a link to the collection, where the four photos already show.
- `templates/page.celestial-paintings.json` shows four products, two columns on desktop, with a banner line. Dawn 16.1.1 accepts `products_to_show` 4 (range 2–25) and `columns_desktop` 2 (range 1–6).
- `celestial-paintings.apply.json` keeps the Nov 5 applied record and adds `pending_revision` `2026-11-06-orion-on-page` with `"applied": false`.

Not done, and not to be done without a yes: replacing the live page body, uploading the template, publishing a theme, reordering the collection, changing any price, touching the sticker or the hidden drafts, or editing NightLens. Shopify admin was not authenticated in this session, so no write was possible from here anyway.

The Ursa Major product description still says the plate was published in 1824. This page and `SPECS.md` say 1825. The draft does not change the product.

## 2026-11-05 record

The page, collection, and main-menu link were published on Nov 5. The first write-up of that morning said Shopify had not accepted them. A later commit recorded the ids after they were applied. The public page JSON matches that later record: page published `2026-11-05T09:00:50-05:00`, collection published `2026-11-05T09:00:38-05:00`. The theme template was written to an unpublished Dawn duplicate only, not to the live theme.

## What the page is

A collection and a content page for the wall-art paintings that are already live Printify posters. Manual order, moon chart first. As of the 2026-11-06 read, Orion is fourth in the collection and is in the repo draft, not yet in the live page body:

| Order | Painting | Handle | Product id | Why this slot |
| --- | --- | --- | --- | --- |
| 1 | Moon Phase | `moon-phase-print` | 15489780777275 | One chart any buyer can hang. Original eight-phase drawing, not a generic row of white circles. |
| 2 | Ursa Major Constellation Print | `ursa-major-constellation-print` | 15489780810043 | The star-map plate already on Printify. Sidney Hall, *Urania's Mirror*, 1825, public domain, on cream atlas paper. A single figure, not a custom night sky. |
| 3 | Solar System Chart Print | `solar-system-chart-print` | 15489779761467 | One celestial atlas plate. Andreas Cellarius, *Harmonia Macrocosmica*, 1660, public domain. |
| 4 | Orion Constellation Print | `orion-constellation-print` | 15490090008891 | Already in the collection as a Printify poster. John Flamsteed, *Atlas Céleste*, Plate 24, 1776, public domain. Added to the repo page draft on 2026-11-06. Not added to the live page body. |

Left off the page: the Solar System kiss-cut sticker (`15489779794235`) and the three hidden `*-original` drafts (`15489621721403`, `15489621754171`, `15489621852475`). Prices stay at the $39.99 already set for 18×24. This page does not change them. There is still no 24×36 variant.

Same-day demand note: `morning-reports/precheck-2026-11-05-trending-products.md`. The gift with the clearest signal there is a personalized star map of one date and one place, then a moon tied to one date. A single public-domain constellation is the weaker cut of that search. This page does not lead with those, because a static Printify poster cannot take a date and a place, and there is no proof step. The live page body still shows the first three. The repo draft adds Orion because that poster is already in the collection and already prints to order. Custom maps stay off the page.

- The eight-phase moon stays first. It is already a Printify poster, and it is the diagram people search as a moon-phase chart. A seller guide calls that row the anchor and says eight plain white circles on black no longer stand out. [Celestial Wall Art for Etsy: What Sells in 2026](https://elistit.com/guides/celestial-wall-art-etsy/) The live file is an original chart on warm paper, which is the distinctive version of that diagram.
- Ursa Major is second because it is the star-map plate already on Printify, not because a single animal outsells a full sky or a custom night. Cream atlas paper, Sidney Hall, 1825.
- The solar-system plate is third: one celestial chart, already printed to order.
- Custom night-sky maps are a real gift business. The Stars Above Co. lists 12,809 sales for that kind of map. [TheStarsAboveCo](https://www.etsy.com/ca/shop/TheStarsAboveCo) The Night Sky lists a $39 print and a company review count in the tens of thousands; that count is the brand, not one poster. See the trending note. Not on this page.
- A twelve-sign series and a full-sky chart are the later paintings in that same note. The plates are not drawn, so they are not listings here.
- Pinterest's 2026 Extra Celestial board is holographic accents, opalescent color, and sci-fi silhouettes. [Extra Celestial](https://www.pinterest.com/pinterestpredicts/extra-celestial/) Apartment Therapy, reporting that forecast, cites an 80 percent rise in "alien core" searches and 115 percent for "opalescent." [Pinterest Predicts 2026 Design Trend Report](https://www.apartmenttherapy.com/pinterest-predicts-2026-37522611) Matte paper cannot flash like foil, and these plates are engraved charts, so the page does not chase that finish.

Orion is no longer only a file in `SPECS.md`. The public product JSON shows a Printify poster, vendor Printify, one variant, 18×24 matte. The Nov 5 note that said not to create a stocked Shopify-only product still stands for anything that is not already on Printify. This draft does not create a product.

## Files

- `pages/celestial-paintings.html` — proposed page body for the 2026-11-06 revision. The live page still has the three-painting body from Nov 5. Do not paste this over the live page without a yes.
- `templates/page.celestial-paintings.json` — Dawn 16.1.1 layout: dark banner, the page copy, then a two-column portrait grid of four products from collection `celestial-paintings`. Vendor hidden. `products_to_show` is 4 and `columns_desktop` is 2, both inside the Dawn 16.1.1 ranges. Not on the live theme.
- `celestial-paintings.apply.json` — Nov 5 record has `"applied": true`. The 2026-11-06 block is `pending_revision` with `"applied": false`.

The live Dawn theme on `bhaeqw-9z` cannot take a theme-file write through the connector. The template belongs on an unpublished copy of Dawn - Celestial. Do not upload it to `duv5f8-wt`.

## Apply the 2026-11-06 revision only after a yes

1. Confirm the domain is `bhaeqw-9z.myshopify.com`. Stop if it is anything else.
2. Re-read the four product ids. Use them only if the handles still match the table above.
3. Do not recreate the collection, the page, or the menu item. They already exist.
4. Do not add the sticker or the draft originals. Do not reorder the collection. Do not change prices.
5. Replace the page body from the HTML file only if Thomas has said yes. Leave the page published state as it already is unless he says otherwise.
6. Copy the template onto the unpublished theme duplicate only. Do not publish the theme, and do not write the live theme.

## Still needs Thomas

- Say yes before the live page body is replaced with the four-painting HTML.
- Say yes before the Dawn template is uploaded, and only to the unpublished theme duplicate.
- Leave prices, collection order, NightLens, the sticker, and the hidden drafts alone.
- A custom date-and-place star map, and a twelve-sign series, are separate jobs. They are not on this page.
- On 2026-11-06 a request to `/password` redirected to the storefront, and the paintings page returned the page itself. The Nov 4 note that the password was still on is out of date. The trial plan was not rechecked. Selling still waits on whatever plan limit he already has noted, until he confirms it.

## Sources

- [Celestial Wall Art for Etsy: What Sells in 2026](https://elistit.com/guides/celestial-wall-art-etsy/) (May 30, 2026)
- [TheStarsAboveCo](https://www.etsy.com/ca/shop/TheStarsAboveCo)
- [Extra Celestial](https://www.pinterest.com/pinterestpredicts/extra-celestial/)
- [Pinterest Predicts 2026 Design Trend Report](https://www.apartmenttherapy.com/pinterest-predicts-2026-37522611)
