import frappe
from frappe import _

from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD


def get_discount_code_refusal(quotation, code: str) -> str | None:
	"""Enforce a link's limits on its own coupon only. Commera then removes the code, so the shopper can still pay full price."""
	link_name = quotation.get(LINK_FIELD)
	if not link_name:
		return None
	link = frappe.get_doc("Buy Link", link_name)
	coupon = link.coupon_code and frappe.db.get_value("Coupon Code", link.coupon_code, "coupon_code")
	if not coupon or code.upper() != coupon.upper():
		return None

	if reason := link.get_unavailable_reason():
		return reason
	if link.once_per_customer and has_used_link(link_name, quotation):
		return _("This offer is limited to one order per customer.")
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
