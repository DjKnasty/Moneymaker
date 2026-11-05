# Store builder pre-check — 2026-11-05

Thomas stopped the telescope-shop work on Nov 5. NightLens on duv5f8-wt was left as it was, and nothing there was edited, published, or priced. This run built the celestial paintings page for the print-on-demand shop bhaeqw-9z instead: three existing Printify posters (Moon Phase, then the Ursa Major star map, then the Solar System chart), page copy, a Dawn page layout, and an unpublished apply file. Shopify never received them. Leaving the telescope shop dropped this session's store connection (`Unauthorized`, then the Shopify server was gone), so the page lives in the repo until the celestial shop is authorized.

## Prepared

- Collection **Celestial Paintings**, handle `celestial-paintings`, manual order, print-on-demand only. No new stocked product.
- Page **Celestial paintings**, handle `celestial-paintings`, body in `shopify/celestial-prints/pages/celestial-paintings.html`. Meant to be created unpublished.
- Layout `shopify/celestial-prints/templates/page.celestial-paintings.json` for Dawn 16.1.1: banner, page copy, three portrait paintings. For an unpublished theme copy only. The connector blocks writes to the live theme.
- Apply sheet `shopify/celestial-prints/celestial-paintings.apply.json` with `"applied": false`.
- Write-up `shopify/celestial-prints/PAINTINGS.md`.

The moon chart leads because it is the diagram already on Printify. Ursa Major is the star-map plate already on Printify, on cream atlas paper. The Cellarius solar system plate is third. The sticker and the hidden draft posters stay off the page. The same day's demand note (`morning-reports/precheck-2026-11-05-trending-products.md`) finds a stronger gift in a custom night sky of one date and place, and in a moon tied to one date. Those are not on this page: a static poster cannot take a date and a place. A twelve-sign set and a full-sky chart are later paintings, and the plates are not drawn. [What sells in celestial wall art, 2026](https://elistit.com/guides/celestial-wall-art-etsy/) [TheStarsAboveCo](https://www.etsy.com/ca/shop/TheStarsAboveCo)

## Not done

- No Shopify mutation ran. No collection, page, menu item, price, or theme file was created.
- Nothing was published.
- Orion, already drawn and held back in `SPECS.md`, was not added. It needs a Printify listing first so the shop still holds no inventory.

## Needs his yes

- Authorize `bhaeqw-9z` and apply the collection and page as unpublished.
- Publish the page, the collection, and a "Celestial paintings" menu link.
- Add the Orion plate in Printify as a fourth painting.
- Leave custom star maps and a zodiac series for a later job.

## Sources

- [Celestial Wall Art for Etsy: What Sells in 2026](https://elistit.com/guides/celestial-wall-art-etsy/) (May 30, 2026)
- [TheStarsAboveCo](https://www.etsy.com/ca/shop/TheStarsAboveCo)
- [Extra Celestial](https://www.pinterest.com/pinterestpredicts/extra-celestial/)
- [Pinterest Predicts 2026 Design Trend Report](https://www.apartmenttherapy.com/pinterest-predicts-2026-37522611)
