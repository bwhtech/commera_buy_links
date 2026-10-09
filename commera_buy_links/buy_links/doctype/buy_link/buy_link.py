import re
import secrets
import string
from urllib.parse import quote, urlencode

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, now_datetime, today

LINK_FIELD = "commera_buy_links_link"
CODE_ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Item codes travel in Commera's /cart/<code>:<qty>,... permalink, so these two characters would split them.
PERMALINK_SEPARATORS = (":", ",")
# Commera's checkout reads these query parameters to fill empty fields: commera/www/cart/checkout.py.
PREFILL_PARAMS = {
	"email": "checkout[email]",
	"first_name": "checkout[shipping_address][first_name]",
	"last_name": "checkout[shipping_address][last_name]",
	"address1": "checkout[shipping_address][address1]",
	"address2": "checkout[shipping_address][address2]",
	"city": "checkout[shipping_address][city]",
	"province": "checkout[shipping_address][province]",
	"country": "checkout[shipping_address][country]",
	"zip": "checkout[shipping_address][zip]",
}
UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")
VISITOR_PARAM_PREFIXES = ("utm_", "checkout[")


class BuyLink(Document):
	def autoname(self):
		self.name = get_new_code()

	def validate(self):
		self.validate_slug()
		self.validate_items()
		if self.starts_on and self.ends_on and get_datetime(self.ends_on) <= get_datetime(self.starts_on):
			frappe.throw(_("Ends on must be after Starts on."))
		if cint(self.usage_limit) < 0:
			frappe.throw(_("Usage limit can't be negative."))

	def validate_slug(self):
		self.slug = (self.slug or "").strip().lower() or None
		if not self.slug:
			return
		if not SLUG_PATTERN.fullmatch(self.slug):
			frappe.throw(
				_("A custom slug uses lowercase letters, digits and single hyphens, for example spring-sale.")
			)
		if frappe.db.exists("Buy Link", self.slug) and self.slug != self.name:
			frappe.throw(_("{0} is already another link's code.").format(self.slug))

	def validate_items(self):
		seen = set()
		for row in self.items:
			if any(separator in row.item_code for separator in PERMALINK_SEPARATORS):
				frappe.throw(_("Row {0}: item codes with : or , can't go in a buy link.").format(row.idx))
			if row.item_code in seen:
				frappe.throw(_("Row {0}: {1} is already in the cart.").format(row.idx, row.item_code))
			if cint(row.qty) < 1:
				frappe.throw(_("Row {0}: the quantity must be at least 1.").format(row.idx))
			seen.add(row.item_code)

	@property
	def path(self) -> str:
		return f"/buy/{self.slug or self.name}"

	@property
	def used_count(self) -> int:
		return frappe.db.count("Sales Order", {LINK_FIELD: self.name, "docstatus": ("<", 2)})

	def get_unavailable_reason(self) -> str | None:
		if self.status != "Active":
			return _("This link isn't active.")
		now = now_datetime()
		if self.starts_on and get_datetime(self.starts_on) > now:
			return _("This offer isn't available yet.")
		if self.ends_on and get_datetime(self.ends_on) <= now:
			return _("This offer is no longer available.")
		if cint(self.usage_limit) and self.used_count >= cint(self.usage_limit):
			return _("This offer has been fully claimed.")
		return None

	def get_cart_url(self, visitor_params: dict | None = None) -> str:
		codes = ",".join(f"{quote(row.item_code, safe='')}:{cint(row.qty)}" for row in self.items)
		params = {param: self.get(field) for field, param in PREFILL_PARAMS.items()}
		params |= {field: self.get(field) for field in UTM_FIELDS}
		if self.coupon_code:
			params["discount"] = frappe.db.get_value("Coupon Code", self.coupon_code, "coupon_code")
		# A visitor's own parameters win, so one link can serve many customers: /buy/abc?checkout[email]=...
		for key, value in (visitor_params or {}).items():
			if key == "discount" or key.startswith(VISITOR_PARAM_PREFIXES):
				params[key] = value
		query = urlencode({key: value for key, value in params.items() if value})
		return f"/cart/{codes}?{query}" if query else f"/cart/{codes}"

	def on_trash(self):
		if orders := self.used_count:
			frappe.throw(
				_("{0} has {1} orders, so it stays for their records. Turn it off instead.").format(
					self.title, orders
				)
			)
		frappe.db.delete("Buy Link Daily Stat", {"link": self.name})

	def record_click(self):
		# One row per link and day, named <link>-<date>, so concurrent clicks add to it instead of racing on a read.
		date = today()
		frappe.db.sql(
			"""insert into `tabBuy Link Daily Stat`
				(name, link, date, clicks, creation, modified, owner, modified_by)
			values (%(name)s, %(link)s, %(date)s, 1, %(now)s, %(now)s, 'Guest', 'Guest')
			on duplicate key update clicks = clicks + 1, modified = %(now)s""",
			{"name": f"{self.name}-{date}", "link": self.name, "date": date, "now": now_datetime()},
		)


def get_new_code() -> str:
	while True:
		code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
		if not frappe.db.exists("Buy Link", code) and not frappe.db.exists("Buy Link", {"slug": code}):
			return code


def get_link_by_code(code: str) -> BuyLink | None:
	name = frappe.db.get_value("Buy Link", {"slug": code.lower()}) or (
		code if frappe.db.exists("Buy Link", code) else None
	)
	return frappe.get_doc("Buy Link", name) if name else None
