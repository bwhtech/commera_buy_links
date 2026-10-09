app_name = "commera_buy_links"
app_title = "Buy Links"
app_publisher = "Hussain Nagaria"
app_description = "Shareable links that fill a Commera cart and send the shopper to checkout"
app_email = "hussain@buildwithhussain.com"
app_license = "mit"

# Send non-GET requests for this app's endpoints as native `application/json`
# bodies instead of form-encoded, per-key JSON-stringified values.
use_json_request_body = True

# Apps
# ------------------

required_apps = ["commera"]
commera_api_version = [1]
commera_plugin_title = "Buy Links"

after_install = "commera_buy_links.install.add_custom_fields"
after_migrate = "commera_buy_links.install.add_custom_fields"

website_route_rules = [{"from_route": "/buy/<code>", "to_route": "buy"}]

doc_events = {"Quotation": {"validate": "commera_buy_links.attribution.attribute_cart"}}

commera_hooks = {"validate_cart": ["commera_buy_links.cart.get_cart_refusal"]}
commera_events = {"order_placed": ["commera_buy_links.orders.on_order_placed"]}

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "commera_buy_links",
# 		"logo": "/assets/commera_buy_links/logo.png",
# 		"title": "Buy Links",
# 		"route": "/commera_buy_links",
# 		"has_permission": "commera_buy_links.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `commera_buy_links/dock/commera_buy_links/commera_buy_links.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/commera_buy_links/css/commera_buy_links.css"
# app_include_js = "/assets/commera_buy_links/js/commera_buy_links.js"

# include js, css files in header of web template
# web_include_css = "/assets/commera_buy_links/css/commera_buy_links.css"
# web_include_js = "/assets/commera_buy_links/js/commera_buy_links.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "commera_buy_links/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "commera_buy_links/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Setup Wizard
# ------------

# open a fresh site's setup in this app's own UI instead of the desk wizard.
# must be a non-desk route (not under /desk or /app); to customize setup within
# desk, use setup_wizard_stages / setup_wizard_complete instead.
# setup_wizard_url = "/commera_buy_links/setup"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "commera_buy_links.utils.jinja_methods",
# 	"filters": "commera_buy_links.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "commera_buy_links.install.before_install"
# after_install = "commera_buy_links.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "commera_buy_links.uninstall.before_uninstall"
# after_uninstall = "commera_buy_links.uninstall.after_uninstall"

# Disable / Enable
# ----------------
# Called when this app is logically disabled or re-enabled on a site,
# without uninstalling it. Use this to hide/restore fields this app adds
# to other apps' doctypes.

# before_disable = "commera_buy_links.uninstall.before_disable"
# after_disable = "commera_buy_links.uninstall.after_disable"
# before_enable = "commera_buy_links.install.before_enable"
# after_enable = "commera_buy_links.install.after_enable"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "commera_buy_links.utils.before_app_install"
# after_app_install = "commera_buy_links.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "commera_buy_links.utils.before_app_uninstall"
# after_app_uninstall = "commera_buy_links.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "commera_buy_links.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "commera_buy_links.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "commera_buy_links.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["commera_buy_links.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"commera_buy_links.tasks.all"
# 	],
# 	"daily": [
# 		"commera_buy_links.tasks.daily"
# 	],
# 	"hourly": [
# 		"commera_buy_links.tasks.hourly"
# 	],
# 	"weekly": [
# 		"commera_buy_links.tasks.weekly"
# 	],
# 	"monthly": [
# 		"commera_buy_links.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "commera_buy_links.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "commera_buy_links.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "commera_buy_links.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "commera_buy_links.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["commera_buy_links.utils.before_request"]
# after_request = ["commera_buy_links.utils.after_request"]

# Job Events
# ----------
# before_job = ["commera_buy_links.utils.before_job"]
# after_job = ["commera_buy_links.utils.after_job"]

# after_file_upload = ["commera_buy_links.utils.after_file_upload"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"commera_buy_links.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
