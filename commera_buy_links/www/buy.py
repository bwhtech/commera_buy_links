import frappe
from frappe import _

from commera_buy_links.attribution import remember_link
from commera_buy_links.buy_links.doctype.buy_link.buy_link import get_link_by_code

no_cache = 1


def get_context(context):
	link = get_link_by_code(frappe.form_dict.get("code") or "")
	if not link:
		raise frappe.PageDoesNotExistError

	context.title = _("Buy link")
	if reason := link.get_unavailable_reason():
		context.message = reason
		return

	link.record_click()
	remember_link(link.name)
	# A GET request is not committed by Frappe; the click must be.
	frappe.db.commit()  # nosemgrep
	frappe.flags.redirect_location = link.get_cart_url(frappe.form_dict)
	# 302, not frappe.redirect's 301: a browser caches a 301 and would skip counting the next click.
	raise frappe.Redirect(302)
