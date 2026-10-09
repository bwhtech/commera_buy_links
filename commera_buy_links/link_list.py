import frappe
from commera.sdk import orders
from frappe.utils import cint, get_url
from pypika import analytics

from commera_buy_links import link_stats
from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD

MAX_PAGE_LENGTH = 100
STATUSES = ("Active", "Draft")
TOP_LINKS = 5


def get_links(
	status: str | None = None,
	search: str | None = None,
	start: int = 0,
	page_length: int = 20,
	period: str = "30d",
) -> dict:
	link = frappe.qb.DocType("Buy Link")
	query = (
		frappe.qb.from_(link)
		.select(link.name, link.title, link.slug, link.status, analytics.Count("*").over().as_("total"))
		.orderby(link.modified, order=frappe.qb.desc)
		.limit(min(cint(page_length) or 20, MAX_PAGE_LENGTH))
		.offset(cint(start))
	)
	if status in STATUSES:
		query = query.where(link.status == status)
	if search := (search or "").strip():
		pattern = f"%{search}%"
		query = query.where(link.title.like(pattern) | link.name.like(pattern) | link.slug.like(pattern))

	rows = query.run(as_dict=True)
	total = rows[0].total if rows else 0
	stats = link_stats.get_link_rows(period, [row.name for row in rows])
	for row in rows:
		row.pop("total")
		row.update(stats[row.name], url=get_link_url(row))
	return {"rows": rows, "total": total}


def get_overview(period: str) -> dict:
	"""Every link together, plus the links that sold the most in the period."""
	names = frappe.get_all("Buy Link", pluck="name")
	rows = link_stats.get_link_rows(period, names)
	titles = dict(frappe.get_all("Buy Link", fields=["name", "title"], as_list=True))
	top = sorted(
		(row | {"title": titles[name]} for name, row in rows.items() if row["sales"]),
		key=lambda row: -row["sales"],
	)
	return link_stats.get_stats(period) | {"top_links": top[:TOP_LINKS]}


def get_link_orders(link_name: str, start: int = 0, page_length: int = 20) -> dict:
	"""Orders placed through one link, newest first, with the stage the Commera dashboard shows."""
	order = frappe.qb.DocType("Sales Order")
	rows = (
		frappe.qb.from_(order)
		.select(
			order.name,
			order.customer_name,
			order.transaction_date,
			order.base_grand_total.as_("total"),
			analytics.Count("*").over().as_("count"),
		)
		.where((order[LINK_FIELD] == link_name) & (order.docstatus < 2))
		.orderby(order.creation, order=frappe.qb.desc)
		.limit(min(cint(page_length) or 20, MAX_PAGE_LENGTH))
		.offset(cint(start))
		.run(as_dict=True)
	)
	total = rows[0].count if rows else 0
	stages = orders.get_orders([row.name for row in rows]) if rows else {}
	for row in rows:
		row.pop("count")
		row.stage = stages.get(row.name, {}).get("stage")
	return {"rows": rows, "total": total}


def get_link_url(link: dict) -> str:
	return get_url(f"/buy/{link.get('slug') or link.get('name')}")
