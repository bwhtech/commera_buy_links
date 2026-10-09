import frappe
from commera.sdk import orders
from commera.sdk.events import CommeraEvent
from frappe.desk.doctype.tag.tag import add_tag
from frappe.utils import cint

from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD


def on_order_placed(event: CommeraEvent) -> None:
	order = orders.get_order(event.reference_name, extra_fields=[LINK_FIELD])
	link_name = order["plugin_fields"][LINK_FIELD]
	if not link_name or not frappe.db.exists("Buy Link", link_name):
		return

	link = frappe.get_doc("Buy Link", link_name)
	# add_tag skips a tag the order already has, so a repeated delivery adds nothing.
	for tag in get_order_tags(link.order_tags):
		add_tag(tag, "Sales Order", order["name"])
	if link.status == "Active" and cint(link.usage_limit) and link.used_count >= cint(link.usage_limit):
		link.db_set("status", "Draft")


def get_order_tags(order_tags: str | None) -> list[str]:
	return [tag.strip() for tag in (order_tags or "").split(",") if tag.strip()]
