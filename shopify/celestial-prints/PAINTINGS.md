# Celestial paintings page

Built 2026-11-05 for the print-on-demand store `bhaeqw-9z.myshopify.com` only. The telescope shop was not edited. Nothing on this page is held in inventory. Printify prints each order.

This run did not write the page into Shopify. The session left the telescope shop on purpose, the next shop check returned `Unauthorized`, and the Shopify connection then dropped (`MCP server does not exist: Shopify`). No collection, page, menu, price, or theme file was created or published. The files below are the page, ready to apply unpublished.

## What the page is

A collection and a content page for three wall-art paintings that are already live Printify posters. Manual order, moon chart first:

| Order | Painting | Handle | Product id | Why this slot |
| --- | --- | --- | --- | --- |
| 1 | Moon Phase | `moon-phase-print` | 15489780777275 | One chart any buyer can hang. Original eight-phase drawing, not a generic row of white circles. |
| 2 | Ursa Major Constellation Print | `ursa-major-constellation-print` | 15489780810043 | The star-map plate already on Printify. Sidney Hall, *Urania's Mirror*, 1825, public domain, on cream atlas paper. A single figure, not a custom night sky. |
| 3 | Solar System Chart Print | `solar-system-chart-print` | 15489779761467 | One celestial atlas plate. Andreas Cellarius, *Harmonia Macrocosmica*, 1660, public domain. |

Left off the page: the Solar System kiss-cut sticker (`15489779794235`) and the three hidden `*-original` drafts (`15489621721403`, `15489621754171`, `15489621852475`). Prices stay at the $39.99 Thomas already set for 18×24. This page does not change them. There is still no 24×36 variant.

Same-day demand note: `morning-reports/precheck-2026-11-05-trending-products.md`. The gift with the clearest signal there is a personalized star map of one date and one place, then a moon tied to one date. A single public-domain constellation is the weaker cut of that search. This page does not lead with those, because a static Printify poster cannot take a date and a place, and there is no proof step. The page shows the three paintings that can ship today with nothing held in stock.

- The eight-phase moon stays first. It is already a Printify poster, and it is the diagram people search as a moon-phase chart. A seller guide calls that row the anchor and says eight plain white circles on black no longer stand out. [Celestial Wall Art for Etsy: What Sells in 2026](https://elistit.com/guides/celestial-wall-art-etsy/) The live file is an original chart on warm paper, which is the distinctive version of that diagram.
- Ursa Major is second because it is the star-map plate already on Printify, not because a single animal outsells a full sky or a custom night. Cream atlas paper, Sidney Hall, 1825.
- The solar-system plate is third: one celestial chart, already printed to order.
- Custom night-sky maps are a real gift business. The Stars Above Co. lists 12,809 sales for that kind of map. [TheStarsAboveCo](https://www.etsy.com/ca/shop/TheStarsAboveCo) The Night Sky lists a $39 print and a company review count in the tens of thousands; that count is the brand, not one poster. See the trending note. Not on this page.
- A twelve-sign series and a full-sky chart are the later paintings in that same note. The plates are not drawn, so they are not listings here.
- Pinterest's 2026 Extra Celestial board is holographic accents, opalescent color, and sci-fi silhouettes. [Extra Celestial](https://www.pinterest.com/pinterestpredicts/extra-celestial/) Apartment Therapy, reporting that forecast, cites an 80 percent rise in "alien core" searches and 115 percent for "opalescent." [Pinterest Predicts 2026 Design Trend Report](https://www.apartmenttherapy.com/pinterest-predicts-2026-37522611) Matte paper cannot flash like foil, and these plates are engraved charts, so the page does not chase that finish.

The finished Orion plate in `SPECS.md` (Flamsteed, 1776) is the next Printify listing if Thomas wants a fourth painting. It was not turned into a Shopify product here, because a product without Printify would be stock this shop does not hold.

## Files

- `pages/celestial-paintings.html` — page body. Unpublished when applied (`isPublished: false`, handle `celestial-paintings`).
- `templates/page.celestial-paintings.json` — Dawn 16.1.1 layout: dark banner, the page copy, then a three-column portrait grid of collection `celestial-paintings`. Vendor hidden. Matches the section settings in Dawn's own `templates/index.json` and `templates/page.json` at tag v16.1.1.
- `celestial-paintings.apply.json` — the unpublished collection, the product order, and the page fields. `"applied": false`.

The live Dawn theme on `bhaeqw-9z` cannot take a theme-file write through the connector. The template belongs on an unpublished copy of Dawn - Celestial. Do not upload it to `duv5f8-wt`.

## Apply when the celestial shop is connected

1. Confirm the domain is `bhaeqw-9z.myshopify.com`. Stop if it is anything else.
2. Re-read the three product ids. Use them only if the handles still match the table above.
3. Create the collection unpublished, handle `celestial-paintings`, sort `MANUAL`, description from the apply file.
4. Add the three products in the listed order. Do not add the sticker or the draft originals.
5. Create the page unpublished, template suffix `celestial-paintings`, body from the HTML file.
6. Copy the template onto an unpublished theme. Do not publish the theme.

## Still needs Thomas

- Say yes before the collection, the page, or a menu link is published. Suggested link, only after the page is published: "Celestial paintings" to `/pages/celestial-paintings`.
- Say yes before Orion is added in Printify.
- A custom date-and-place star map, and a twelve-sign series, are separate jobs. They are not on this page.
- Trial plan and the storefront password are unchanged. Selling still waits on the plan upgrade he already has noted in the store README.

## Sources

- [Celestial Wall Art for Etsy: What Sells in 2026](https://elistit.com/guides/celestial-wall-art-etsy/) (May 30, 2026)
- [TheStarsAboveCo](https://www.etsy.com/ca/shop/TheStarsAboveCo)
- [Extra Celestial](https://www.pinterest.com/pinterestpredicts/extra-celestial/)
- [Pinterest Predicts 2026 Design Trend Report](https://www.apartmenttherapy.com/pinterest-predicts-2026-37522611)
