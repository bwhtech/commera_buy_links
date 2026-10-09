import frappe

from commera_buy_links import link_editor, link_list, link_stats
from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD


@frappe.whitelist(methods=["GET"])
def get_links(
	status: str | None = None,
	search: str | None = None,
	start: int = 0,
	page_length: int = 20,
	period: str = "30d",
) -> dict:
	frappe.has_permission("Buy Link", "read", throw=True)
	return link_list.get_links(status, search, start, page_length, period)


@frappe.whitelist(methods=["GET"])
def get_overview(period: str = "30d") -> dict:
	frappe.has_permission("Buy Link", "read", throw=True)
	return link_list.get_overview(period)


@frappe.whitelist(methods=["GET"])
def get_link_stats(name: str, period: str = "30d") -> dict:
	frappe.has_permission("Buy Link", "read", doc=name, throw=True)
	return link_stats.get_stats(period, [name])


@frappe.whitelist(methods=["GET"])
def get_link_orders(name: str, start: int = 0, page_length: int = 20) -> dict:
	frappe.has_permission("Sales Order", "read", throw=True)
	return link_list.get_link_orders(name, start, page_length)


@frappe.whitelist(methods=["GET"])
def get_link(name: str) -> dict:
	frappe.has_permission("Buy Link", "read", doc=name, throw=True)
	return link_editor.get_link(name)


@frappe.whitelist(methods=["POST"])
def save_link(link: dict) -> str:
	if link.get("name"):
		frappe.has_permission("Buy Link", "write", doc=link["name"], throw=True)
	else:
		frappe.has_permission("Buy Link", "create", throw=True)
	return link_editor.save_link(link)


@frappe.whitelist(methods=["POST"])
def duplicate_link(name: str) -> str:
	frappe.has_permission("Buy Link", "create", throw=True)
	return link_editor.duplicate_link(name)


@frappe.whitelist(methods=["POST"])
def delete_link(name: str) -> None:
	frappe.delete_doc("Buy Link", name)


@frappe.whitelist(methods=["GET"])
def search_items(search: str | None = None, product: str | None = None) -> list[dict]:
	frappe.has_permission("Buy Link", "read", throw=True)
	return link_editor.search_items(search, product)


@frappe.whitelist(methods=["GET"])
def search_coupon_codes(search: str | None = None) -> list[dict]:
	frappe.has_permission("Coupon Code", "read", throw=True)
	return link_editor.search_coupon_codes(search)


@frappe.whitelist(methods=["GET"])
def get_order_link(sales_order: str) -> dict | None:
	frappe.has_permission("Sales Order", "read", doc=sales_order, throw=True)
	link_name = frappe.db.get_value("Sales Order", sales_order, LINK_FIELD)
	if not link_name or not frappe.db.exists("Buy Link", link_name):
		return None
	link = frappe.get_doc("Buy Link", link_name)
	return {
		"name": link.name,
		"title": link.title,
		"path": link.path,
		"coupon": frappe.db.get_value("Coupon Code", link.coupon_code, "coupon_code")
		if link.coupon_code
		else None,
		"utm": {
			field: link.get(field)
			for field in ("utm_source", "utm_medium", "utm_campaign")
			if link.get(field)
		},
	}
