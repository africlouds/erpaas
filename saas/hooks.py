# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "saas"
app_title = "ERPNext as a Service"
app_publisher = "Africlouds Ltd"
app_description = "Manage creating ERP instances as a service, integrates with CRM and Sales module"
app_icon = "octicon octicon-file-directory"
app_color = "green"
app_email = "arwema@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/saas/css/saas.css"
# app_include_js = "/assets/saas/js/saas.js"

# include js, css files in header of web template
# web_include_css = "/assets/saas/css/saas.css"
# web_include_js = "/assets/saas/js/saas.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "saas.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "saas.install.before_install"
# after_install = "saas.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "saas.notifications.get_notification_config"

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

doc_events = {
 	"Site": {
 		"after_insert": "saas.api.notify_user",
		"on_trash": "saas.api.delete_account"
	}
}
# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"saas.tasks.all"
# 	],
# 	"daily": [
# 		"saas.tasks.daily"
# 	],
# 	"hourly": [
# 		"saas.tasks.hourly"
# 	],
# 	"weekly": [
# 		"saas.tasks.weekly"
# 	]
# 	"monthly": [
# 		"saas.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "saas.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "saas.event.get_events"
# }

