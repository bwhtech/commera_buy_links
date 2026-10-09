import frappe

from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD


def order_has_link(doctype: str, name: str) -> bool:
	return bool(frappe.db.get_value("Sales Order", name, LINK_FIELD))
