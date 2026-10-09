# Gaps

What the Shopify app [Checkout Links](https://checkoutlinks.com) does that this plugin does not, and what Commera is missing to close each gap.

## Commera platform gaps

| Gap | Effect on this plugin | What Commera needs |
| --- | --- | --- |
| No SDK call to build a cart on the server | The plugin redirects to Commera's `/cart/<codes>` permalink, so the cart is built in the browser | `commera.sdk.cart` functions to set cart lines, apply a coupon and set customer fields |
| No SDK hook or field to attribute a cart to a source | The plugin reads its own cookie in a Quotation `validate` doc event | A supported way to tag a cart from a request, for example a `cart_created` hook or `set_cart_fields` for guests |
| Prefill has no phone field | Phone cannot be prefilled | `checkout[shipping_address][phone]` in `CHECKOUT_PREFILL_PARAMS` |
| The permalink always goes to checkout (or to the cart for guests without guest checkout) | No cart-page or product-page destination | A `?return_to=` parameter on the permalink |
| The permalink replaces the cart | No "add to the current cart" mode | A merge option on the permalink |
| No promotion API | Only an existing Coupon Code works. No automatic discount, free shipping or free gift per link | An SDK or hook for link-scoped discounts. `cart_fees` cannot be negative |
| No hook can remove a coupon | A limit hit at checkout refuses the cart and asks the shopper to remove the code | A hook that can drop a discount with a message |
| The SDK has no product search or images | The dashboard picker queries Item directly and shows no images | `catalog.search_items` with image and option |
| No SDK test fixtures | Tests build their own Items, Customers and Sales Orders | Public test helpers for a store order and a cart |

## Features not built yet

| Feature | Note |
| --- | --- |
| Promotion types: automatic discount, free shipping, free gift | Needs the promotion API above |
| Line discounts and line attributes | Commera cart lines have no attributes |
| Selling plans (subscriptions) | Commera has no selling plans |
| Popup page before checkout (upsells, countdown, consent) | Could be a Commera theme page |
| Passcode and require-login links | Possible in `/buy` before the redirect |
| Link preview (Open Graph title, description, image) | Possible: render meta tags on `/buy` for bots, redirect people |
| Dynamic links (`li=` cart lines, customer shortcodes, Klaviyo) | Prefill per visitor works through `checkout[...]` parameters; lines do not |
| Templates and saved views | Duplicate works; templates do not |
| Reorder links from an order or customer | Could be an order action and a customer action |
| Theme button block | Needs a Commera theme block API |
| Analytics export | Stats show in the dashboard only |
| Bot filtering | Link-preview crawlers (WhatsApp, Slack) count as clicks |
| QR styles and PNG/PDF export | Plain SVG only |

## Found while testing on the dev site

- The demo data prices the server cart at about 96 times the storefront price (₹4,831.53 for a ₹49.99 item). The price list currency and the store currency do not match. The storefront shows ₹149.97 and checkout shows ₹14,494.59 for the same cart.
