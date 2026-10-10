# Notes on the reference app

Buy Links is modelled on the Shopify app **Checkout Links**. These notes record what that app does, from its public pages, as of October 2026. [GAPS.md](GAPS.md) lists what Buy Links does not do yet.

## Sources

| Source | URL |
| --- | --- |
| Homepage | https://checkoutlinks.com |
| Help centre (63 articles) | https://checkoutlinks.com/help |
| Popup help (15 articles) | https://checkoutlinks.com/help/popup |
| Popup in the link editor | https://checkoutlinks.com/help/link-editor/popup |
| Shopify App Store listing | https://apps.shopify.com/checkoutlinks |
| Clicks in Shopify reports | https://checkoutlinks.com/blog/how-to-see-checkout-link-clicks-in-shopify-reports |

The help articles have no screenshots. The homepage draws an HTML mock of the popup in its "A mini landing page over your own store" section. The App Store screenshots show shopper scenarios, for example "Gifting link lets creators pick products and check out free".

## Product

- One plan, $25 a month, every feature included, 7-day trial. Free on development stores.
- Made in Stockholm. Launched 2022. 5.0 from 36 reviews. Built for Shopify, 2025 Build Award.
- The app is a Shopify sales channel, so products and discounts must be published to it.

## The link

A link is `yourstore.com/<SHORTCODE>`, or a custom slug that redirects to `/a/link/<SHORTCODE>`. The shortcode is 6 characters and does not change. A click builds the cart and opens Shopify checkout, or opens the popup first.

Link editor sections, top to bottom:

| Section | Fields |
| --- | --- |
| Link | Name (internal), shortcode, URL with copy, custom slug, status Active or Draft |
| Cart | Products and variants with quantity, selling plan, per-line discount, line attributes; drag to reorder; "Reorder items" from the customer's last order |
| Promotions | Discount (% or fixed, with message), free shipping, free gift, existing discount code. Applies to the whole cart, the link's items, a collection or products. Up to 2 conditions (cart quantity or total). Only the largest discount applies |
| Dynamic | URL parameters: `li=VARIANT:QTY[:PLAN]`, `c=` customer (shortcode, Shopify ID, Klaviyo profile or inline fields), `attr=`, `note=` |
| B2B | Customer signs in for company prices and terms |
| Tag orders | Up to 250 tags, added to completed orders |
| Attribution | UTM source, medium, campaign, term, content, ref, custom parameters. Stored as order metafields `cl_utm_*`, `cl_ref`, `cl_custom_*`, `cl_shortcode` |
| Usage limit | Total uses (at the cap the link becomes Draft) and once per customer (by email or account; checkout is blocked with a message). Shown as "42 of 50 used · 8 left" |
| Schedule | Start and end, store time zone. Outside the window: "not yet available" or "no longer available" |
| Passcode | 4-digit code screen |
| Popup | Toggle, then Edit opens the block editor |
| Scripts | Custom JavaScript on the popup page |
| Link preview | Title, description, image (1200×630) for shared links |
| QR code | 6 styles (Square, Rounded, Dots, Classy, Classy rounded, Extra rounded), colour, PNG/SVG/PDF. Always points to `/a/link/<SHORTCODE>` |

## Analytics

- Four numbers per link: clicks, orders, sales, conversion rate, for today, 7 days or 30 days. They are also sortable columns on the links list.
- No charts in the app. Deeper reporting goes to Shopify: each click is a `link_visited` app event, and orders carry the metafields above for ShopifyQL.
- Their own note: app-event sessions and raw clicks do not match exactly.

## Popup

> "The Popup opens on top of your storefront, with no theme changes and no page builder. Customers review the offer, grab an upsell, and hit checkout in one place."

What the shopper sees (homepage mock): one card over the blurred store. A dashed callout ("Your second bottle is on us. Pick your size."), cart lines with a size picker and quantity, a free-gift line at $0, subtotal, discount with its promotion name, shipping, total, **Go to checkout**, and "Skip offer and continue shopping".

The builder: a per-link Popup toggle, then a block editor with the block list on the left and a live preview on the right. Add block (a menu with descriptions), drag to reorder, hide, delete. A colour scheme for the whole popup. Two templates, **Influencer gifting** and **Build a box**, that replace the blocks and can set the link's promotions.

| Block | Required | Settings |
| --- | --- | --- |
| Logo | Yes | Store logo or name |
| Cart items | Yes, can be hidden | Preloaded products; per-item discount and min/max quantity; cart min/max; list or "slots" (build a box) |
| Cart summary | Yes | Subtotal, shipping, total |
| Checkout button | Yes | Text (default "Go to checkout"), button and text colour |
| Callout | No, many | Rich text, 7 colour presets or custom, solid or dotted border |
| Countdown | No, one | 1 to 1,440 minutes; text with `{{ timer }}`; at zero sends the shopper to the store |
| Consent | No, one | Label and terms (slide-up panel). Their checkout button stays disabled until ticked |
| Upsells | No, many | Products or a collection; list or 2/3-column grid; variant picker, Add, per-product discount; "Recommended" source |
| Skip button | No | Text link to the store |
| Media | No, many | Image or banner |
| Progress bar | No, one | Tiers from the link's promotions, locked and unlocked labels |
| Kaching Bundles | No | Third-party bundles |

Fixed positions: logo and cart items at the top, consent just above the checkout button, optional blocks above the cart summary.

## Admin

- Links page: Create link; views All, Dynamic, Active, Draft, plus saved custom views; filter by status and type; search by name or shortcode; columns Updated, Name, Shortcode, Status, Type, Clicks, Orders, Conversion rate, Sales; a Templates tab.
- Link templates: save a link as a template, or create a link from one.
- Quick create from a product, the product list, an order ("Reorder - #N") and a customer.

## Integrations

Help articles cover Klaviyo, Downpay, Kaching Bundles, Shopify POS and ManyChat. The homepage also names Postscript, Attentive, Recharge, Appstle, Loop, Gorgias, Flow, and Meta, Google and TikTok ads.

## How Buy Links differs

| Area | Buy Links |
| --- | --- |
| URL | `/buy/<code>` or `/buy/<slug>` on the store domain |
| Discounts | An existing ERPNext Coupon Code only ([#223](https://github.com/bwhtech/commera/issues/223)) |
| Analytics | The same four numbers, plus charts in the dashboard: daily trend, click-to-checkout-to-order funnel, top links, by-day table, and today/7/30/90 days |
| Popup | A fixed layout: message, cart with quantities, coupon, countdown, consent, Checkout, Skip. Live preview of the real storefront. The checkout button stays enabled and says what to fix |
| QR code | Square, Rounded or Dots in a store colour; SVG, PNG and PDF |
