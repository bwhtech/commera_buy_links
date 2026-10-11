# Gaps

What the Shopify app [Checkout Links](https://checkoutlinks.com) does that this plugin does not, and the Commera issue for each platform gap. [notes.md](notes.md) has the research on the reference app.

## Commera platform gaps

| Gap | Effect on this plugin | Issue |
| --- | --- | --- |
| Checkout's `discount` parameter applies only an ERPNext Coupon Code | A link cannot carry a Commera Discount code, so there is no automatic discount, free shipping or free gift per link, and the popup names the coupon ("SAVE10 at checkout") instead of the amount | None yet |
| Checkout prefill has no phone | Phone cannot be prefilled | [#245](https://github.com/bwhtech/commera/issues/245) |
| The SDK has no product search, images or cart lines | The dashboard picker queries Item directly and shows no images. The popup reads cart lines through the internal `commera.www.cart.permalink.get_cart_lines` | [#248](https://github.com/bwhtech/commera/issues/248) |
| No SDK test helpers; `before_tests` needs a dedicated test site | Tests build their own Items, Customers and Sales Orders | [#250](https://github.com/bwhtech/commera/issues/250) |
| The `/` to `/en` redirect drops the query string | `/buy/<code>` builds `/<lang>?buy=...` itself | [#252](https://github.com/bwhtech/commera/issues/252) |

## Features not built yet

| Feature | Note |
| --- | --- |
| Promotion types: automatic discount, free shipping, free gift | Needs Commera Discount codes in the `discount` parameter |
| Line attributes and a cart built on the server | Commera has `cart.add_lines` and `cart.set_cart_attributes` ([#254](https://github.com/bwhtech/commera/pull/254)). The plugin still fills the cart through the cart link and tags the order through its own cookie |
| Selling plans (subscriptions) | Commera has no selling plans |
| Popup blocks beyond the fixed layout: upsells, media, progress bar, size picker, drag-to-reorder, templates | The popup has a fixed layout with switches for consent and countdown |
| Passcode and require-login links | Possible in `/buy` before the redirect |
| Link preview (Open Graph title, description, image) | Possible: render meta tags on `/buy` for bots, redirect people |
| Dynamic links (`li=` cart lines, customer shortcodes, Klaviyo) | Prefill per visitor works through `checkout[...]` parameters; lines do not |
| Templates and saved views | Duplicate works; templates do not |
| Reorder links from an order or customer | Could be an order action and a customer action |
| Theme button block | Needs a Commera theme block API |
| Analytics export | Stats show in the dashboard only |
| Bot filtering | Link-preview crawlers (WhatsApp, Slack) count as clicks |
| QR styles beyond Square, Rounded and Dots | The reference app has six styles |

## Found while testing on the dev site

- The demo data prices the server cart at about 96 times the storefront price (₹4,831.53 for a ₹49.99 item). The price list currency and the store currency do not match. The storefront shows ₹149.97 and checkout shows ₹14,494.59 for the same cart.
