import re

import frappe
from commera.branding import get_configured_brand_assets
from frappe import _
from frappe.model.document import Document

HEX_COLOUR = re.compile(r"^#[0-9A-Fa-f]{6}$")
# The PNG and PDF downloads draw the logo with Pillow, which cannot read SVG.
RASTER_LOGO = (".png", ".jpg", ".jpeg", ".webp")
EDITABLE_FIELDS = ("attribution_days", "qr_style", "qr_color", "qr_background", "qr_logo", "qr_logo_image")


class BuyLinksSettings(Document):
	def validate(self):
		# Each settings row saves on its own, so a blank colour is allowed and falls back to the default.
		for field in ("qr_color", "qr_background"):
			if self.get(field) and not HEX_COLOUR.fullmatch(self.get(field)):
				frappe.throw(
					_("{0} must be a hex colour such as #111827.").format(self.meta.get_label(field))
				)
		self.validate_logo()

	def validate_logo(self):
		if self.qr_logo == "Store logo" and not get_store_logo():
			frappe.throw(_("Your store has no PNG, JPG or WebP logo. Upload a logo for the QR code instead."))
		if self.qr_logo != "Upload":
			return
		if not self.qr_logo_image:
			frappe.throw(_("Upload a logo image, or pick another logo option."))
		if not self.qr_logo_image.lower().endswith(RASTER_LOGO):
			frappe.throw(_("The QR logo must be a PNG, JPG or WebP image."))

	def get_values(self) -> dict:
		return {field: self.get(field) for field in EDITABLE_FIELDS} | {"store_logo": get_store_logo()}

	def set_values(self, values: dict) -> None:
		self.update({field: values[field] for field in EDITABLE_FIELDS if field in values})

	def get_logo_url(self) -> str | None:
		if self.qr_logo == "Store logo":
			return get_store_logo()
		if self.qr_logo == "Upload":
			return self.qr_logo_image or None
		return None


def get_store_logo() -> str | None:
	"""The storefront's own logo, when it is an image the QR code can draw."""
	logo = get_configured_brand_assets()["logo"]
	return logo if logo.lower().endswith(RASTER_LOGO) else None
