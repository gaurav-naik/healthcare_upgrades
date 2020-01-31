# Copyright (c) 2016, Inqubit Systems and Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldtype": "Link", "fieldname": "name", "options":"Sales Invoice", "label":"Invoice Name", "width":120},
		{"fieldtype": "Link", "fieldname": "customer", "options":"Customer", "label":"Customer","width":120 },
		{"fieldtype": "Data", "fieldname": "customer_name", "label":"Customer Name" ,"width":250},
		{"fieldtype": "Currency", "fieldname": "total_amount", "label": "Total Sales", "width":120 },
	]


def get_data(filters):
	doctor_condition = ""
	if filters.get("physician"):
		doctor_condition = " AND si.idr_physician = '{0}'".format(
			frappe.db.escape(filters.get("physician"))
		)

	query = """
		select
			si.name as name,
			si.customer as customer,
			si.customer_name as customer_name,
			sum(sii.net_amount) as total_amount,
			si.posting_date as posting_date
		from `tabSales Invoice Item` sii inner join `tabSales Invoice` si
		on sii.parent = si.name
		where sii.item_group = "ISTOLOGICI"
		{doctor_condition}
		and si.posting_date between '{from_date}' and '{to_date}'
		and si.docstatus = 1
		group by si.name, si.customer, si.customer_name, si.posting_date;
	""".format(
		doctor_condition=doctor_condition,
		from_date=filters.get("from_date"),
		to_date=filters.get("to_date")
	)
	return frappe.db.sql(query, debug=True)
