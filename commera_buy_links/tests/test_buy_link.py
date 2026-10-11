import io
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import frappe
from commera.checkout_hooks import get_discount_code_refusal as commera_discount_code_refusal
from commera.sdk import STORE_ORDER_TYPE
from commera.sdk.events import CommeraEvent
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, getdate, now_datetime
from PIL import Image

from commera_buy_links.api import download_qr, get_popup, get_qr_preview
from commera_buy_links.attribution import COOKIE, attribute_cart
from commera_buy_links.buy_links.doctype.buy_link.buy_link import (
	LINK_FIELD,
	get_link_by_code,
)
from commera_buy_links.cart import get_discount_code_refusal
from commera_buy_links.link_stats import get_stats
from commera_buy_links.orders import on_order_placed
from commera_buy_links.qr_code import QrCode, QrStyle

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

	def test_limits_refuse_only_the_links_own_coupon(self):
		coupon = make_coupon()
		link = make_link(coupon_code=coupon, once_per_customer=1)
		make_order(link.name, "repeat@example.com")
		repeat_cart = make_cart(link.name, coupon, "repeat@example.com")

		self.assertIn("one order per customer", get_discount_code_refusal(repeat_cart, COUPON.lower()))
		self.assertIsNone(get_discount_code_refusal(repeat_cart, "SOME-OTHER-CODE"))
		self.assertIsNone(get_discount_code_refusal(make_cart(link.name, coupon, "new@example.com"), COUPON))
		self.assertIsNone(get_discount_code_refusal(make_cart(None, coupon, "repeat@example.com"), COUPON))

	def test_a_closed_link_refuses_its_coupon_with_the_shoppers_reason(self):
		coupon = make_coupon()
		link = make_link(coupon_code=coupon, ends_on=add_days(now_datetime(), -1))
		reason = get_discount_code_refusal(make_cart(link.name, coupon, "late@example.com"), COUPON)
		self.assertEqual(reason, link.get_unavailable_reason())

	def test_commera_asks_the_link_before_it_applies_the_coupon(self):
		coupon = make_coupon()
		link = make_link(coupon_code=coupon, status="Draft")
		cart = make_cart(link.name, coupon, "draft@example.com")
		cart.flags = frappe._dict()
		self.assertEqual(commera_discount_code_refusal(cart, COUPON), link.get_unavailable_reason())

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


class TestPopup(IntegrationTestCase):
	def set_storefront(self, enabled: bool):
		frappe.db.set_value(
			"Commera Storefront App",
			{"parent": "Commera Settings", "app": "commera_buy_links"},
			"enabled",
			int(enabled),
		)

	def test_the_popup_lands_on_the_store_only_when_the_storefront_runs_it(self):
		link = make_link(popup_enabled=1)

		self.set_storefront(True)
		self.assertTrue(link.get_landing_url().startswith(f"/{frappe.local.lang or 'en'}?buy={link.name}"))

		self.set_storefront(False)
		self.assertTrue(link.get_landing_url().startswith("/cart/"))

		self.set_storefront(True)
		link.popup_enabled = 0
		self.assertTrue(link.get_landing_url().startswith("/cart/"))

	def test_shoppers_get_an_active_link_only(self):
		draft = make_link(status="Draft", popup_enabled=1)
		frappe.set_user("Guest")
		self.addCleanup(frappe.set_user, "Administrator")

		self.assertIn("isn't active", get_popup(draft.name)["unavailable"])
		with self.assertRaises(frappe.PermissionError):
			get_popup(draft.name, preview=1)

	def test_staff_preview_a_draft_with_its_settings(self):
		draft = make_link(status="Draft", popup_enabled=1, popup_callout="Hello", popup_consent=1)

		popup = get_popup(draft.name, preview=1)

		self.assertEqual(popup["popup_callout"], "Hello")
		self.assertEqual(popup["popup_consent"], 1)
		self.assertIn("query", popup)


class TestQrCode(IntegrationTestCase):
	URL = "https://store.example.com/buy/spring-sale"

	def test_each_format_is_a_real_file(self):
		code = QrCode(self.URL, QrStyle())
		self.assertTrue(code.get_file("svg").startswith(b"<svg"))
		self.assertTrue(code.get_file("png").startswith(b"\x89PNG"))
		self.assertTrue(code.get_file("pdf").startswith(b"%PDF"))
		with self.assertRaises(frappe.ValidationError):
			code.get_file("gif")

	def test_only_data_modules_turn_into_dots(self):
		square = QrCode(self.URL, QrStyle(shape="Square")).get_svg()
		dots = QrCode(self.URL, QrStyle(shape="Dots"))

		self.assertNotIn("<circle", square)
		svg = dots.get_svg()
		modules = [shape for shape in dots.get_shapes() if shape[0] == "module"]
		self.assertEqual(svg.count("<circle"), len(modules))
		# Three finders plus this version's alignment patterns stay squares, each drawn as three rects.
		self.assertEqual(svg.count("<rect") - 1, len(dots.patterns) * 3)

	def test_settings_refuse_a_colour_that_is_not_hex(self):
		settings = frappe.get_single("Buy Links Settings")
		settings.qr_color = "red"
		with self.assertRaises(frappe.ValidationError):
			settings.validate()
		settings.qr_color = ""
		settings.validate()

	def test_a_logo_raises_error_correction_and_is_drawn_in_every_format(self):
		logo = make_logo_file()
		plain = QrCode(self.URL, QrStyle())
		branded = QrCode(self.URL, QrStyle(logo=logo.file_url))

		self.assertGreater(branded.version, plain.version)
		self.assertIn("<image", branded.get_svg())
		self.assertNotEqual(branded.get_file("png"), QrCode(self.URL, QrStyle(logo=None)).get_file("png"))
		self.assertTrue(branded.get_file("pdf").startswith(b"%PDF"))

	def test_settings_refuse_a_logo_the_downloads_cannot_draw(self):
		settings = frappe.get_single("Buy Links Settings")
		settings.update({"qr_color": "", "qr_background": "", "qr_logo": "Upload", "qr_logo_image": ""})
		with self.assertRaises(frappe.ValidationError):
			settings.validate()
		settings.qr_logo_image = "/files/logo.svg"
		with self.assertRaises(frappe.ValidationError):
			settings.validate()
		settings.qr_logo_image = "/files/logo.png"
		settings.validate()
		self.assertEqual(settings.get_logo_url(), "/files/logo.png")

	def test_preview_draws_unsaved_values_without_saving_them(self):
		stored = frappe.db.get_single_value("Buy Links Settings", "qr_style")
		values = {"qr_style": "Dots", "qr_color": "#1E3A8A", "qr_background": "#FFFFFF", "qr_logo": "None"}

		svg = get_qr_preview(values)

		self.assertIn("<circle", svg)
		self.assertIn('fill="#1E3A8A"', svg)
		self.assertEqual(frappe.db.get_single_value("Buy Links Settings", "qr_style"), stored)
		with self.assertRaises(frappe.ValidationError):
			get_qr_preview(values | {"qr_color": "blue"})

	def test_download_answers_with_a_file(self):
		link = make_link(slug=f"qr-{frappe.generate_hash(length=4).lower()}")
		download_qr(link.name, "png")
		self.assertEqual(frappe.local.response["type"], "download")
		self.assertEqual(frappe.local.response["filename"], f"buy-link-{link.slug}.png")
		with self.assertRaises(frappe.ValidationError):
			download_qr(link.name, "exe")


def make_logo_file():
	buffer = io.BytesIO()
	Image.new("RGB", (64, 64), "#EA580C").save(buffer, "PNG")
	return frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"logo-{frappe.generate_hash(length=6)}.png",
			"content": buffer.getvalue(),
		}
	).insert()
