from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import frappe
from commera.sdk import STORE_ORDER_TYPE
from commera.sdk.events import CommeraEvent
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, getdate, now_datetime

from commera_buy_links.attribution import COOKIE, attribute_cart
from commera_buy_links.buy_links.doctype.buy_link.buy_link import (
	LINK_FIELD,
	get_link_by_code,
)
from commera_buy_links.cart import get_cart_refusal
from commera_buy_links.link_stats import get_stats
from commera_buy_links.orders import on_order_placed

COUPON = "CL-TEST-10"


def make_item() -> str:
	item_code = f"CL-TEST {frappe.generate_hash(length=6)}"
	frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": item_code,
			"item_name": item_code,
			"item_group": frappe.db.get_value("Item Group", {"is_group": 0}),
			"stock_uom": "Nos",
			"is_stock_item": 0,
		}
	).insert(ignore_permissions=True)
	return item_code


def make_coupon() -> str:
	if name := frappe.db.get_value("Coupon Code", {"coupon_code": COUPON}):
		return name
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	pricing_rule = frappe.get_doc(
		{
			"doctype": "Pricing Rule",
			"title": COUPON,
			"apply_on": "Transaction",
			"selling": 1,
			"coupon_code_based": 1,
			"rate_or_discount": "Discount Percentage",
			"discount_percentage": 10,
			"company": company,
		}
	).insert(ignore_permissions=True)
	return (
		frappe.get_doc(
			{
				"doctype": "Coupon Code",
				"coupon_name": COUPON,
				"coupon_code": COUPON,
				"coupon_type": "Promotional",
				"pricing_rule": pricing_rule.name,
			}
		)
		.insert(ignore_permissions=True)
		.name
	)


def make_link(**values):
	return frappe.get_doc(
		{
			"doctype": "Buy Link",
			"title": "Test link",
			"status": "Active",
			"items": [{"item_code": make_item(), "qty": 2}],
		}
		| values
	).insert(ignore_permissions=True)


def make_order(link_name: str, email: str) -> str:
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	customer = frappe.get_doc(
		{"doctype": "Customer", "customer_name": f"CL Test {frappe.generate_hash(length=6)}"}
	).insert(ignore_permissions=True)
	order = frappe.get_doc(
		{
			"doctype": "Sales Order",
			"customer": customer.name,
			"company": company,
			"order_type": STORE_ORDER_TYPE,
			"transaction_date": getdate(),
			"delivery_date": getdate(),
			"contact_email": email,
			"items": [{"item_code": make_item(), "qty": 1, "rate": 100}],
			LINK_FIELD: link_name,
		}
	)
	order.flags.ignore_permissions = True
	order.insert()
	return order.name


class FakeCart(SimpleNamespace):
	"""A Quotation stand-in: frappe._dict can't hold a field called items, which shadows dict.items."""

	def get(self, fieldname, default=None):
		return getattr(self, fieldname, default)

	def set(self, fieldname, value):
		setattr(self, fieldname, value)


def make_cart(link_name: str | None, coupon_code: str | None, email: str = "", item_codes=()) -> FakeCart:
	return FakeCart(
		**{
			"order_type": STORE_ORDER_TYPE,
			"coupon_code": coupon_code,
			"contact_email": email,
			"party_name": None,
			"items": [SimpleNamespace(item_code=item_code) for item_code in item_codes],
			LINK_FIELD: link_name,
		}
	)


class TestBuyLink(IntegrationTestCase):
	def test_cart_url_carries_items_discount_prefill_and_visitor_overrides(self):
		coupon = make_coupon()
		link = make_link(coupon_code=coupon, email="link@example.com", first_name="Asha", utm_source="ig")

		url = urlsplit(
			link.get_cart_url({"checkout[email]": "visitor@example.com", "code": "x", "evil": "1"})
		)
		query = parse_qs(url.query)

		item_code = link.items[0].item_code
		self.assertEqual(url.path, f"/cart/{item_code.replace(' ', '%20')}:2")
		self.assertEqual(query["discount"], [COUPON])
		self.assertEqual(query["checkout[email]"], ["visitor@example.com"])
		self.assertEqual(query["checkout[shipping_address][first_name]"], ["Asha"])
		self.assertEqual(query["utm_source"], ["ig"])
		self.assertNotIn("evil", query)
		self.assertNotIn("code", query)

	def test_a_link_opens_by_code_or_slug(self):
		link = make_link(slug=f"Spring-{frappe.generate_hash(length=4).lower()}")
		self.assertEqual(link.slug, link.slug.lower())
		self.assertEqual(get_link_by_code(link.name).name, link.name)
		self.assertEqual(get_link_by_code(link.slug.upper()).name, link.name)
		self.assertIsNone(get_link_by_code("does-not-exist"))

	def test_validation_refuses_bad_slugs_items_and_dates(self):
		with self.assertRaises(frappe.ValidationError):
			make_link(slug="Not a slug!")
		item_code = make_item()
		with self.assertRaises(frappe.ValidationError):
			make_link(items=[{"item_code": item_code, "qty": 1}, {"item_code": item_code, "qty": 1}])
		with self.assertRaises(frappe.ValidationError):
			make_link(starts_on=now_datetime(), ends_on=add_days(now_datetime(), -1))

	def test_unavailable_reasons(self):
		self.assertIsNone(make_link().get_unavailable_reason())
		self.assertIn("isn't active", make_link(status="Draft").get_unavailable_reason())
		self.assertIn(
			"isn't available yet", make_link(starts_on=add_days(now_datetime(), 1)).get_unavailable_reason()
		)
		self.assertIn("no longer", make_link(ends_on=add_days(now_datetime(), -1)).get_unavailable_reason())

		limited = make_link(usage_limit=1)
		make_order(limited.name, "first@example.com")
		self.assertIn("fully claimed", limited.get_unavailable_reason())

	def test_attribution_needs_the_cookie_and_one_of_the_links_items(self):
		link = make_link()
		request = SimpleNamespace(cookies={COOKIE: link.name})

		with patch.object(frappe.local, "request", request, create=True):
			unrelated = make_cart(None, None, item_codes=[make_item()])
			attribute_cart(unrelated)
			self.assertIsNone(unrelated.get(LINK_FIELD))

			related = make_cart(None, None, item_codes=[link.items[0].item_code])
			attribute_cart(related)
			self.assertEqual(related.get(LINK_FIELD), link.name)

	def test_limits_refuse_only_while_the_links_coupon_is_on_the_cart(self):
		coupon = make_coupon()
		link = make_link(coupon_code=coupon, once_per_customer=1)
		make_order(link.name, "repeat@example.com")

		self.assertIn(
			"one order per customer", get_cart_refusal(make_cart(link.name, coupon, "repeat@example.com"))
		)
		self.assertIsNone(get_cart_refusal(make_cart(link.name, None, "repeat@example.com")))
		self.assertIsNone(get_cart_refusal(make_cart(link.name, coupon, "new@example.com")))

	def test_order_placed_tags_the_order_and_closes_a_full_link(self):
		link = make_link(usage_limit=1, order_tags="influencer, spring")
		order_name = make_order(link.name, "buyer@example.com")
		event = CommeraEvent(
			id=f"{order_name}-order_placed",
			name="order_placed",
			reference_doctype="Sales Order",
			reference_name=order_name,
			data={},
			created_at=now_datetime(),
		)

		on_order_placed(event)
		on_order_placed(event)

		tags = frappe.db.get_value("Sales Order", order_name, "_user_tags").strip(",").split(",")
		self.assertEqual(sorted(tags), ["influencer", "spring"])
		self.assertEqual(frappe.db.get_value("Buy Link", link.name, "status"), "Draft")


class TestLinkStats(IntegrationTestCase):
	def test_clicks_on_one_day_add_to_one_row(self):
		link = make_link()
		link.record_click()
		link.record_click()

		rows = frappe.get_all("Buy Link Daily Stat", filters={"link": link.name}, fields=["clicks"])
		self.assertEqual([row.clicks for row in rows], [2])

	def test_stats_count_the_period_and_the_one_before_it(self):
		link = make_link()
		link.record_click()
		insert_clicks(link.name, add_days(getdate(), -8), 5)
		make_order(link.name, "stats@example.com")

		stats = get_stats("7d", [link.name])

		self.assertEqual(len(stats["series"]), 7)
		self.assertEqual(stats["totals"]["clicks"], 1)
		self.assertEqual(stats["totals"]["orders"], 1)
		self.assertEqual(stats["totals"]["conversion"], 100)
		self.assertEqual(stats["previous"]["clicks"], 5)
		self.assertEqual(stats["series"][-1]["clicks"], 1)

	def test_a_link_with_orders_cannot_be_deleted(self):
		link = make_link()
		make_order(link.name, "kept@example.com")
		with self.assertRaises(frappe.ValidationError):
			frappe.delete_doc("Buy Link", link.name)

	def test_deleting_an_unused_link_removes_its_clicks(self):
		link = make_link()
		link.record_click()
		frappe.delete_doc("Buy Link", link.name)
		self.assertFalse(frappe.db.exists("Buy Link Daily Stat", {"link": link.name}))


def insert_clicks(link_name: str, day, clicks: int):
	frappe.get_doc(
		{
			"doctype": "Buy Link Daily Stat",
			"name": f"{link_name}-{day}",
			"link": link_name,
			"date": day,
			"clicks": clicks,
		}
	).db_insert()
