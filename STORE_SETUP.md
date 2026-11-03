# NightLens store foundation

Connected shop: `duv5f8-wt.myshopify.com` (Advanced, USD)  
Working brand (from catalog/pages): **NightLens** — smart telescopes & field gear  
Admin shop display name still shows **My Store** (rename in Shopify Admin → Settings → Store details)

## Done in this pass

| Area | Status |
| --- | --- |
| Theme | Live theme is **Drive** (Horizon family — clean Online Store 2.0). Unpublished: `NightLens`, `NasdaqBeast - Alphalete layout (draft)`. Theme publish via API is blocked; switch in Admin → Online Store → Themes if you prefer NightLens. |
| Home | Theme index template (`/`) — Horizon/Drive homepage with catalog collections |
| Collection | Live collections: Smart Telescopes, Accessories, Travel Gear (+ Home page / frontpage) |
| Product | Active NightLens products published to Online Store (sample/mock catalog) |
| About | `/pages/about` — About NightLens (published) |
| Contact | `/pages/contact` — support content filled + published |
| Shipping & Returns | `/pages/shipping-returns` — published |
| Main menu | Home → Smart Telescopes → Travel Gear → Accessories → About → Contact → Shipping & Returns |
| Footer menu | About → Contact → Shipping & Returns → Smart Telescopes → Search |
| Checkout policies | Full refund policy written in `LEGAL_REFUND_POLICY.md` and published on `/pages/shipping-returns`. Official checkout Refund policy still needs paste in Admin → Settings → Policies (API lacks `write_legal_policies` scope). |
| Shipping rates | General profile: Domestic Standard + Express active |
| Payments (wallets) | Shop Pay, Apple Pay, Google Pay supported on plan |
| Customer accounts | New customer accounts; login optional at checkout |

## Customer purchase flow (cart → checkout → confirmation)

Shopify provides this path by default on Online Store + Checkout — no custom app required for the basic flow.

1. **Browse** — Home `/` or a collection (e.g. `/collections/smart-telescopes`)
2. **Product** — open a product (e.g. NightLens Pro) → choose variant → **Add to cart**
3. **Cart** — cart drawer/page → review qty → **Checkout**
4. **Checkout** — email/contact → shipping address → shipping method (Standard/Express) → payment (card / Shop Pay / Apple Pay / Google Pay)
5. **Confirmation** — Thank you / order status page; customer can create/sign in to account for order history (`customerAccountsVersion: NEW_CUSTOMER_ACCOUNTS`)

**Smoke-test checklist (do once in Admin password-protected storefront or after going live):**

- [ ] Add NightLens Pro to cart from product page
- [ ] Open cart → Checkout
- [ ] Complete a **Bogus Gateway** or test-mode payment order (enable in Settings → Payments if needed)
- [ ] Confirm Thank you page loads and order appears in Admin → Orders
- [ ] Optional: create customer account and view order under Account → Orders

## Still needed from you

Reply with only these three (or confirm the working defaults):

1. **Brand name** — keep **NightLens**, use repo name **Moneymaker**, or something else?
2. **Niche** — confirm **smart telescopes / astronomy gear**, or different?
3. **Domain** — keep `duv5f8-wt.myshopify.com` for now, or preferred custom domain (e.g. `nightlens.com`)?

## Remaining merchant checklist (Admin)

- [ ] Rename shop from **My Store** → final brand name
- [ ] Connect/buy custom domain (Settings → Domains)
- [ ] Publish preferred theme if not Drive
- [ ] Replace sample/mock products with real inventory, prices, and stock
- [ ] Archive leftover “Example product” drafts if unused
- [ ] Set weight/dimensions on products so shipping quotes stay accurate
- [ ] Confirm tax settings (Settings → Taxes)
- [ ] Confirm payment provider is production-ready (not test/Bogus) before real sales
- [ ] Review Privacy Policy brand wording (still says “My Store”)
- [ ] Password-protect vs. remove storefront password when ready to sell

## Useful URLs

- Storefront: https://duv5f8-wt.myshopify.com
- About: https://duv5f8-wt.myshopify.com/pages/about
- Contact: https://duv5f8-wt.myshopify.com/pages/contact
- Shipping & Returns: https://duv5f8-wt.myshopify.com/pages/shipping-returns
- Customer account: https://shopify.com/103940948336/account
