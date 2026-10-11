# Gaps

What the Shopify app [Checkout Links](https://checkoutlinks.com) does that this plugin does not, and the Commera issue for each platform gap. [notes.md](notes.md) has the research on the reference app.

## Commera platform gaps

| Gap | Effect on this plugin | Issue |
| --- | --- | --- |
| No SDK call to build a cart on the server | The plugin redirects to Commera's `/cart/<codes>` permalink, so the cart is built in the browser | [#223](https://github.com/bwhtech/commera/issues/223) |
| No supported way to tag a guest's cart with a source | The plugin sets its own cookie at `/buy/<code>` and tags the Quotation in its `validate` doc event | [#223](https://github.com/bwhtech/commera/issues/223) |
| No promotion API | Only an existing Coupon Code works. No automatic discount, free shipping or free gift per link | [#223](https://github.com/bwhtech/commera/issues/223) |
| Checkout prefill has no phone | Phone cannot be prefilled | [#245](https://github.com/bwhtech/commera/issues/245) |
| The SDK has no product search, images or cart lines | The dashboard picker queries Item directly and shows no images. The popup reads cart lines through the internal `commera.www.cart.permalink.get_cart_lines` | [#248](https://github.com/bwhtech/commera/issues/248) |
| No coupon amount before checkout | The popup names the coupon ("SAVE10 at checkout") instead of the discount amount | [#249](https://github.com/bwhtech/commera/issues/249) |
| No SDK test helpers; `before_tests` needs a dedicated test site | Tests build their own Items, Customers and Sales Orders | [#250](https://github.com/bwhtech/commera/issues/250) |
| The `/` to `/en` redirect drops the query string | `/buy/<code>` builds `/<lang>?buy=...` itself | [#252](https://github.com/bwhtech/commera/issues/252) |

## Features not built yet

| Feature | Note |
| --- | --- |
| Promotion types: automatic discount, free shipping, free gift | Needs the promotion API above |
| Line discounts and line attributes | Commera cart lines have no attributes |
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
