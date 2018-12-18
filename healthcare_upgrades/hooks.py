# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "healthcare_upgrades"
app_title = "Healthcare Upgrades"
app_publisher = "Inqubit"
app_description = "Upgrades to Healthcare Module of ERPNext"
app_icon = "fa fa-medkit"
app_color = "#da251d"
app_email = "info@inqubit.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/healthcare_upgrades/css/healthcare_upgrades.css"
# app_include_js = "/assets/healthcare_upgrades/js/healthcare_upgrades.js"

# include js, css files in header of web template
# web_include_css = "/assets/healthcare_upgrades/css/healthcare_upgrades.css"
# web_include_js = "/assets/healthcare_upgrades/js/healthcare_upgrades.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Patient" : "public/js/hu_patient.js",
    "Patient Appointment": "public/js/hu_patient_appointment.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {
    "Patient Appointment" : "public/js/patient_appointment_calendar.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "healthcare_upgrades.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "healthcare_upgrades.install.before_install"
# after_install = "healthcare_upgrades.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "healthcare_upgrades.notifications.get_notification_config"

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
	"Patient": {
		"on_update": "healthcare_upgrades.hu_patient.on_update",
	},
    "Physician": {
        "validate": "healthcare_upgrades.hu_physician.validate",
    },
    "Patient Appointment": {
        "on_update": "healthcare_upgrades.hu_patient_appointment.on_update",
    },
    "Sales Invoice": {
		"on_submit": "healthcare_upgrades.hu_sales_invoice.on_submit",
		"validate": "healthcare_upgrades.hu_sales_invoice.validate",
		"on_cancel": "healthcare_upgrades.hu_sales_invoice.on_cancel",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"healthcare_upgrades.tasks.all"
# 	],
# 	"daily": [
# 		"healthcare_upgrades.tasks.daily"
# 	],
# 	"hourly": [
# 		"healthcare_upgrades.tasks.hourly"
# 	],
# 	"weekly": [
# 		"healthcare_upgrades.tasks.weekly"
# 	]
# 	"monthly": [
# 		"healthcare_upgrades.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "healthcare_upgrades.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "healthcare_upgrades.event.get_events"
# }
override_whitelisted_methods = {
	"erpnext.healthcare.doctype.patient_appointment.patient_appointment.create_invoice":"healthcare_upgrades.hu_patient_appointment.create_invoice"
}

fixtures = [
    {
        "dt":"Custom Field", 
        "filters": [[
            "name", "in", [
                "Patient-hu_sb_basic_info",
                "Patient-hu_last_name",
                "Patient-hu_first_name",
                "Patient-hu_cb_basic_info_1",
                "Patient-hu_phone_no",
                "Physician-hu_physician_schedule",
                "Physician-hu_appointment_color",
                "Patient Appointment-hu_procedure",
                "Patient Appointment-hu_procedure_name",
                "Patient Appointment-hu_appointment_color",
                "Patient Appointment-hu_appointment_end_datetime",
                "Patient Appointment-hu_appointment_description",
                "Sales Invoice-hu_physician",
                "Sales Invoice-hu_mode_of_payment",
                "Sales Invoice-hu_payment_entry_reference",
                "Sales Invoice-hu_sb_appointment_details",
                "Sales Invoice-hu_diagnoses",
                "Sales Invoice-hu_cb_appointment_details_1",
                "Sales Invoice-hu_appointment_from_time",
                "Sales Invoice-hu_appointment_to_time"
            ]
        ]]
    },
    {
        "dt":"Property Setter", 
        "filters": [[
            "name", "in", [
                "Physician-physician_schedule-hidden",
                "Patient Appointment-check_availability-hidden"
            ]
        ]]
    },
]