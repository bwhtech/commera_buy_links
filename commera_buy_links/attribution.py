import frappe
from commera.sdk import STORE_ORDER_TYPE
from frappe.utils import cint

from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD

COOKIE = "commera_buy_link"
SECONDS_PER_DAY = 86400


def remember_link(link_name: str):
	days = cint(frappe.db.get_single_value("Buy Links Settings", "attribution_days")) or 7
	frappe.local.cookie_manager.set_cookie(COOKIE, link_name, max_age=days * SECONDS_PER_DAY, httponly=True)


def attribute_cart(doc, method=None):
	"""Quotation validate: tag a store cart with the link the shopper last opened."""
	if doc.order_type != STORE_ORDER_TYPE or doc.get(LINK_FIELD):
		return
	request = getattr(frappe.local, "request", None)
	link_name = request.cookies.get(COOKIE) if request else None
	if not link_name:
		return

	# Only a cart that still holds one of the link's items counts, so a later unrelated purchase is not credited.
	link_items = frappe.get_all(
		"Buy Link Item", filters={"parenttype": "Buy Link", "parent": link_name}, pluck="item_code"
	)
	if set(link_items) & {row.item_code for row in doc.items}:
		doc.set(LINK_FIELD, link_name)
