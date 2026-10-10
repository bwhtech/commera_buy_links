import frappe
from commera.branding import get_configured_brand_assets
from commera.www.cart.permalink import get_cart_lines
from frappe.utils import cint

from commera_buy_links.buy_links.doctype.buy_link.buy_link import BuyLink

DRAFT_FIELDS = (
	"popup_callout",
	"popup_button_label",
	"popup_skip_label",
	"popup_consent",
	"popup_consent_label",
	"popup_consent_terms",
	"popup_countdown",
	"popup_countdown_minutes",
	"popup_countdown_text",
)


def get_popup(link: BuyLink, visitor_params: dict | None = None) -> dict:
	"""What the storefront script draws: the store, the link's cart and the popup's own settings."""
	settings = frappe.get_cached_doc("Commera Settings")
	notices = []
	# Commera's permalink lines carry the shopper-facing title, image, price and stock, so the popup matches the cart.
	lines = get_cart_lines({row.item_code: cint(row.qty) for row in link.items}, notices)
	return {
		"code": link.name,
		"store_name": settings.get("store_name") or frappe.defaults.get_global_default("company"),
		"logo": get_configured_brand_assets()["logo"] or None,
		"currency": frappe.db.get_single_value("Global Defaults", "default_currency"),
		"lines": [get_line(line) for line in lines],
		"notices": notices,
		"coupon": frappe.db.get_value("Coupon Code", link.coupon_code, "coupon_code")
		if link.coupon_code
		else None,
		"query": link.get_cart_query(visitor_params),
	} | {field: link.get(field) for field in DRAFT_FIELDS}


def get_line(line: dict) -> dict:
	images = line["item"].get("images") or []
	stock = cint(line["variant"]["stock_detail"].get("stock_qty"))
	return {
		"item_code": line["variant"]["item_code"],
		"title": line["item"].get("display_name") or line["variant"]["item_name"],
		"size": line["variant"].get("size"),
		"image": images[0]["image"] if images else None,
		"qty": line["qty"],
		"max_qty": stock,
		"price": line["price"],
		"default_price": line["default_price"],
	}
