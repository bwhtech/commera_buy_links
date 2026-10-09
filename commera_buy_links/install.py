from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from commera_buy_links.buy_links.doctype.buy_link.buy_link import LINK_FIELD


def add_custom_fields():
	link_field = {
		"fieldname": LINK_FIELD,
		"label": "Buy Link",
		"fieldtype": "Link",
		"options": "Buy Link",
		"insert_after": "order_type",
		"read_only": 1,
		"module": "Buy Links",
	}
	# Same fieldname on both: ERPNext's Quotation to Sales Order mapper copies it across.
	create_custom_fields(
		{"Quotation": [link_field], "Sales Order": [link_field | {"search_index": 1}]}, update=True
	)
