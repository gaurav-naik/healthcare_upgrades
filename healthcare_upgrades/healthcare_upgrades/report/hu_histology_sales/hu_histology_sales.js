// Copyright (c) 2016, Inqubit Systems and Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["HU Histology Sales"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"physician",
			"label": __("Doctor"),
			"fieldtype": "Link",
			"options": "Physician"
		},
	]
}
