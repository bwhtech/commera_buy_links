import frappe
from frappe import _

from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD


def get_cart_refusal(quotation) -> str | None:
	"""Enforce a link's limits only while its coupon is on the cart: removing the code always lets the shopper pay full price."""
	link_name = quotation.get(LINK_FIELD)
	if not link_name:
		return None
	link = frappe.get_doc("Buy Link", link_name)
	if not link.coupon_code or quotation.get("coupon_code") != link.coupon_code:
		return None

	coupon = frappe.db.get_value("Coupon Code", link.coupon_code, "coupon_code")
	if reason := link.get_unavailable_reason():
		return _("{0} Remove the discount code {1} to check out at full price.").format(reason, coupon)
	if link.once_per_customer and has_used_link(link_name, quotation):
		return _(
			"This offer is limited to one order per customer. Remove the discount code {0} to check out at full price."
		).format(coupon)
	return None


def has_used_link(link_name: str, quotation) -> bool:
	filters = {LINK_FIELD: link_name, "docstatus": ("<", 2)}
	if quotation.get("contact_email") and frappe.db.exists(
		"Sales Order", filters | {"contact_email": quotation.contact_email}
	):
		return True
	return bool(
		quotation.get("party_name")
		and frappe.db.exists("Sales Order", filters | {"customer": quotation.party_name})
	)
