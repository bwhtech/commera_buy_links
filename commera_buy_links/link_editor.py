import frappe
from commera.sdk import catalog
from frappe import _
from frappe.utils import cint

from commera_buy_links.buy_links.doctype.buy_link.buy_link import BuyLink, is_storefront_enabled
from commera_buy_links.link_list import get_link_url
from commera_buy_links.qr_code import QrCode

EDITABLE_FIELDS = (
	"title",
	"status",
	"slug",
	"coupon_code",
	"email",
	"first_name",
	"last_name",
	"address1",
	"address2",
	"city",
	"province",
	"zip",
	"country",
	"utm_source",
	"utm_medium",
	"utm_campaign",
	"utm_term",
	"utm_content",
	"order_tags",
	"usage_limit",
	"once_per_customer",
	"starts_on",
	"ends_on",
	"popup_enabled",
	"popup_callout",
	"popup_button_label",
	"popup_skip_label",
	"popup_consent",
	"popup_consent_label",
	"popup_consent_terms",
	"popup_countdown",
	"popup_countdown_minutes",
	"popup_countdown_text",
)
SEARCH_LIMIT = 20


def get_link(name: str) -> dict:
	link: BuyLink = frappe.get_doc("Buy Link", name)
	values = {field: link.get(field) for field in ("name", *EDITABLE_FIELDS)}
	url = get_link_url(values)
	return values | {
		"url": url,
		"used_count": link.used_count,
		"storefront_enabled": is_storefront_enabled(),
		"unavailable_reason": link.get_unavailable_reason(),
		"items": get_item_details({row.item_code: cint(row.qty) for row in link.items}),
		"coupon": frappe.db.get_value("Coupon Code", link.coupon_code, "coupon_code")
		if link.coupon_code
		else None,
		"qr_svg": QrCode(url).get_svg(),
	}


def save_link(values: dict) -> str:
	link = frappe.get_doc("Buy Link", values["name"]) if values.get("name") else frappe.new_doc("Buy Link")
	link.update({field: values.get(field) for field in EDITABLE_FIELDS if field in values})
	link.set(
		"items",
		[{"item_code": row["item_code"], "qty": cint(row["qty"])} for row in values.get("items") or []],
	)
	link.save()
	return link.name


def duplicate_link(name: str) -> str:
	link = frappe.copy_doc(frappe.get_doc("Buy Link", name))
	link.update({"title": _("Copy of {0}").format(link.title), "status": "Draft", "slug": None})
	link.insert()
	return link.name


def get_item_details(quantities: dict[str, int]) -> list[dict]:
	items = catalog.get_items(list(quantities))
	images = dict(
		frappe.get_all(
			"Item", filters={"name": ("in", list(quantities))}, fields=["name", "image"], as_list=True
		)
	)
	return [
		{
			"item_code": item_code,
			"qty": qty,
			"title": items[item_code]["title"] if item_code in items else item_code,
			"price": items[item_code]["price"] if item_code in items else None,
			"is_listed": bool(items.get(item_code, {}).get("is_listed")),
			"image": images.get(item_code),
		}
		for item_code, qty in quantities.items()
	]


def search_items(search: str | None = None, product: str | None = None) -> list[dict]:
	"""Sellable size-level items, the codes a Commera cart holds."""
	filters = {"disabled": 0, "has_variants": 0}
	if product:
		filters["variant_of"] = product
	or_filters = None
	if search := (search or "").strip():
		or_filters = {"item_name": ("like", f"%{search}%"), "item_code": ("like", f"%{search}%")}
	codes = frappe.get_all(
		"Item",
		filters=filters,
		or_filters=or_filters,
		pluck="name",
		order_by="item_name asc",
		limit=SEARCH_LIMIT * 3,
	)
	listed = [detail for detail in get_item_details(dict.fromkeys(codes, 1)) if detail["is_listed"]]
	return listed[:SEARCH_LIMIT]


def search_coupon_codes(search: str | None = None) -> list[dict]:
	filters = {"coupon_code": ("like", f"%{search.strip()}%")} if search and search.strip() else {}
	return frappe.get_all(
		"Coupon Code",
		filters=filters,
		fields=["name", "coupon_code", "coupon_name", "valid_upto", "used", "maximum_use"],
		order_by="creation desc",
		limit=SEARCH_LIMIT,
	)
