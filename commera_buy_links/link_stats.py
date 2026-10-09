from datetime import date, timedelta

import frappe
from frappe.query_builder import functions
from frappe.utils import cint, flt, getdate

from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD

PERIOD_DAYS = {"today": 1, "7d": 7, "30d": 30, "90d": 90}


class Period:
	"""The last `days` days up to today, and the same span just before it for comparison."""

	def __init__(self, period: str):
		if period not in PERIOD_DAYS:
			frappe.throw(frappe._("Period must be one of {0}").format(", ".join(PERIOD_DAYS)))
		days = PERIOD_DAYS[period]
		self.end = getdate()
		self.start = self.end - timedelta(days=days - 1)
		self.previous_end = self.start - timedelta(days=1)
		self.previous_start = self.previous_end - timedelta(days=days - 1)

	@property
	def dates(self) -> list[date]:
		return [self.start + timedelta(days=offset) for offset in range((self.end - self.start).days + 1)]


def get_stats(period: str, link_names: list[str] | None = None) -> dict:
	"""Clicks, carts that reached checkout, orders and sales per day, with totals and the previous period."""
	span = Period(period)
	clicks = get_clicks_by_day(span.start, span.end, link_names)
	orders = get_orders_by_day(span.start, span.end, link_names)
	series = [
		{
			"date": str(day),
			"clicks": clicks.get(day, 0),
			"orders": orders.get(day, {}).get("orders", 0),
			"sales": orders.get(day, {}).get("sales", 0),
		}
		for day in span.dates
	]
	return {
		"series": series,
		"totals": get_totals(span.start, span.end, link_names),
		"previous": get_totals(span.previous_start, span.previous_end, link_names),
	}


def get_totals(start: date, end: date, link_names: list[str] | None = None) -> dict:
	clicks = sum(get_clicks_by_day(start, end, link_names).values())
	day_orders = get_orders_by_day(start, end, link_names).values()
	orders = sum(row["orders"] for row in day_orders)
	return {
		"clicks": clicks,
		"checkouts": get_checkout_count(start, end, link_names),
		"orders": orders,
		"sales": sum(row["sales"] for row in day_orders),
		"conversion": get_conversion(orders, clicks),
	}


def get_link_rows(period: str, link_names: list[str]) -> dict[str, dict]:
	"""Totals per link for the list page."""
	if not link_names:
		return {}
	span = Period(period)
	stat = frappe.qb.DocType("Buy Link Daily Stat")
	clicks = dict(
		frappe.qb.from_(stat)
		.select(stat.link, functions.Sum(stat.clicks))
		.where(stat.link.isin(link_names) & stat.date[span.start : span.end])
		.groupby(stat.link)
		.run()
	)
	order = frappe.qb.DocType("Sales Order")
	link_column = order[LINK_FIELD]
	orders = {
		row.link: row
		for row in get_order_query(span.start, span.end, link_names)
		.select(link_column.as_("link"))
		.groupby(link_column)
		.run(as_dict=True)
	}
	return {name: get_row(cint(clicks.get(name)), orders.get(name)) for name in link_names}


def get_row(clicks: int, order_row: dict | None) -> dict:
	orders = cint(order_row.orders) if order_row else 0
	return {
		"clicks": clicks,
		"orders": orders,
		"sales": flt(order_row.sales) if order_row else 0,
		"conversion": get_conversion(orders, clicks),
	}


def get_lifetime_clicks(link_name: str) -> int:
	return cint(frappe.db.get_value("Buy Link Daily Stat", {"link": link_name}, "sum(clicks)"))


def get_clicks_by_day(start: date, end: date, link_names: list[str] | None) -> dict[date, int]:
	stat = frappe.qb.DocType("Buy Link Daily Stat")
	query = (
		frappe.qb.from_(stat)
		.select(stat.date, functions.Sum(stat.clicks))
		.where(stat.date[start:end])
		.groupby(stat.date)
	)
	if link_names is not None:
		query = query.where(stat.link.isin(link_names or [""]))
	return {getdate(day): cint(count) for day, count in query.run()}


def get_orders_by_day(start: date, end: date, link_names: list[str] | None) -> dict[date, dict]:
	order = frappe.qb.DocType("Sales Order")
	rows = (
		get_order_query(start, end, link_names)
		.select(order.transaction_date.as_("day"))
		.groupby(order.transaction_date)
		.run(as_dict=True)
	)
	return {getdate(row.day): {"orders": cint(row.orders), "sales": flt(row.sales)} for row in rows}


def get_order_query(start: date, end: date, link_names: list[str] | None):
	order = frappe.qb.DocType("Sales Order")
	link_column = order[LINK_FIELD]
	query = (
		frappe.qb.from_(order)
		.select(functions.Count("*").as_("orders"), functions.Sum(order.base_grand_total).as_("sales"))
		.where((order.docstatus < 2) & link_column.isnotnull() & (link_column != ""))
		.where(order.transaction_date[start:end])
	)
	if link_names is not None:
		query = query.where(link_column.isin(link_names or [""]))
	return query


def get_checkout_count(start: date, end: date, link_names: list[str] | None) -> int:
	"""Store carts tagged with a link: the shopper got as far as checkout, where Commera saves the cart."""
	cart = frappe.qb.DocType("Quotation")
	link_column = cart[LINK_FIELD]
	query = (
		frappe.qb.from_(cart)
		.select(functions.Count("*"))
		.where(link_column.isnotnull() & (link_column != ""))
		.where(functions.Date(cart.creation)[start:end])
	)
	if link_names is not None:
		query = query.where(link_column.isin(link_names or [""]))
	return cint(query.run()[0][0])


def get_conversion(orders: int, clicks: int) -> float:
	return round(orders / clicks * 100, 1) if clicks else 0
