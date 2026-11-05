# Theme & storefront changes — bhaeqw-9z ("My Store")
Date: 2026-11-04 (America/New_York). Connector: user-Shopify--account-2 (confirmed myshopifyDomain = bhaeqw-9z.myshopify.com).

## Theme
- NEW INSTALL: free Shopify **Dawn 16.1.1** (official GitHub release zip), pre-configured locally, uploaded via
  stagedUploadsCreate (FILE, application/zip) -> multipart POST (201) -> themeCreate.
  - Theme: "Dawn - Celestial"  gid://shopify/OnlineStoreTheme/188589113659  role UNPUBLISHED
  - Horizon gid://shopify/OnlineStoreTheme/188559425851 still MAIN (untouched; becomes the backup once Dawn is published).
- **NOT PUBLISHED**: themePublish is refused by the connector's safety policy ("Publishing a theme is blocked here ... ask them to
  publish it in Shopify admin"). Thomas: Admin > Online Store > Themes > "Dawn - Celestial" > ... > Publish.
- Style: color schemes — scheme-1 navy #0B1220 / text #EDE8DC / gold buttons #C2A469; scheme-2 #121B2D (cards/sections);
  scheme-3 near-black #06080E (hero, size strip, announcement, footer); scheme-4 cream; scheme-5 gold.
  Headings Cormorant 600 (cormorant_n6, scale 120), body Assistant 400 (scale 105), square buttons/pills, page width 1400.

## Homepage (templates/index.json)
1. Hero image-banner: solar-system-mockup.jpg (existing shop file), 50% overlay, "Vintage celestial art" + subhead
   ("Star charts and engravings from the 17th and 19th centuries, plus an original moon phase chart, printed on demand on
   matte fine art paper."), buttons Shop all prints / About the art.
2. Featured collection "The prints" — All Prints, 3 columns, portrait, secondary image on hover.
3. Multicolumn "About the art" — Ursa Major (Sidney Hall, Urania's Mirror, London 1820s), Solar System (Cellarius,
   Harmonia Macrocosmica, Amsterdam 1660), Moon Phases (original chart); links to products + About.
4. Rich-text size strip: "18 × 24 in · 24 × 36 in", paper, unframed in tube, frames in photos not included.
- No newsletter popup; footer newsletter disabled, Follow-on-Shop off.

## Header/footer
- Announcement bar: "Printed on demand · Ships unframed in a rigid tube" -> /pages/shipping-returns
- Header: logo top-center, main-menu, country/language selectors off.
- Footer: text block "Celestial prints" + "Help" link list (footer menu); policies shown, payment icons on.

## Product template
- Removed vendor ("Printify") line; size selector = button pills; gallery thumbnail_slider (mobile thumbnails on), lightbox zoom,
  contain fit; collapsibles "Sizes & paper" and "Shipping & returns" (page); related "More prints" (3, portrait).

## Store content (live regardless of theme)
- Collection "All Prints" /collections/all-prints (gid://shopify/Collection/512813596987), manual, 3 products.
- Pages: About (/pages/about), Shipping & Returns (/pages/shipping-returns) — generic, no timeframes;
  Contact (/pages/contact, template page.contact, intro text updated).
- Main menu: Home / Shop all prints / About. Footer menu: Shipping & Returns / Contact / Search / Your Privacy Choices.
- Product descriptions reformatted only (intro paragraphs + Details list; added "frame shown in photos not included").
  Prices/variants/SKUs verified unchanged: 18x24 $44.99, 24x36 $64.99.

## TODO for Thomas (admin only)
- Publish "Dawn - Celestial" in admin; preview first via Customize.
- Store name (still "My Store"); set store policies (Settings > Policies) so footer policy links appear.
- Check inventory: variants show inventoryQuantity 0 — make sure tracking is off / continue selling for Printify.
- Note: product copy says Urania's Mirror "1824"; SPECS.md says plate dated 1825. Site copy uses "1820s" on homepage/About.

## Branding (Celestial Atlas Prints)

_2026-11-04 (ET), store bhaeqw-9z. MAIN theme = "Dawn - Celestial" (gid://shopify/OnlineStoreTheme/188589113659); Horizon is unpublished._

Done:
- Brand art: `celestial-atlas-prints-wordmark.png` (911x135, transparent, #EDE8DC Cormorant Garamond semibold, thin #C2A469 rule with a small star) and `celestial-atlas-prints-favicon.png` (512x512, gold star on #0B1220).
- Uploaded to Shopify Files (READY):
  - shopify://shop_images/celestial-atlas-prints-wordmark.png (MediaImage 49555097485627)
  - shopify://shop_images/celestial-atlas-prints-favicon.png (MediaImage 49555097518395)
- About page: first sentence now reads "At Celestial Atlas Prints, we make wall art from the history of astronomy." Nothing else changed.
- No "My Store" text in templates/index.json or any page.

NOT applied (blocked):
- themeFilesUpsert on the live theme was refused by the connector's safety policy ("Theme file writes against the live storefront are blocked").
  - config/settings_data.json `current`: logo = shopify://shop_images/celestial-atlas-prints-wordmark.png, logo_width 90 -> 260, favicon = shopify://shop_images/celestial-atlas-prints-favicon.png
  - sections/footer-group.json: footer text heading "Celestial prints" -> "Celestial Atlas Prints"

Admin TODO:
- Theme editor > Header: pick the wordmark as the logo and set the width to about 260. Theme settings > Logo/Favicon: pick the favicon. Footer text block: change the heading to "Celestial Atlas Prints".
- Settings > Store details: rename "My Store" to "Celestial Atlas Prints".
