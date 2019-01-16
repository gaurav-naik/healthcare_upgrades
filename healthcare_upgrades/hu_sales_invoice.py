import frappe
from frappe import _

def on_submit(doc, method):
	#create payment entry
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
	new_payment_entry = get_payment_entry(doc.doctype, doc.name)
	new_payment_entry.mode_of_payment = doc.mode_of_payment
	#new_payment_entry.paid_to = frappe.db.get_value("Mode of Payment Account", {"company":doc.company, "parent":doc.hu_mode_of_payment}, "default_account")
	#new_payment_entry.paid_to_account_currency = frappe.db.get_value("Account", {"account_name":new_payment_entry.paid_to}, "account_currency")
	new_payment_entry.reference_no = "-"
	new_payment_entry.reference_date = doc.posting_date or frappe.utils.getdate()
	new_payment_entry.save()
	new_payment_entry.submit()

	frappe.db.set_value("Sales Invoice", doc.name, "hu_payment_entry_reference", new_payment_entry.name)

def validate(doc, method):
	if not doc.mode_of_payment:
		frappe.throw(_("Please set Mode of Payment."))

def on_cancel(doc, method):
	payment_entry = frappe.get_doc("Payment Entry", doc.hu_payment_entry_reference)
	payment_entry.cancel()
	frappe.db.commit()

	frappe.delete_doc("Payment Entry", payment_entry.name)
	frappe.msgprint(_("Payment entry " + doc.hu_payment_entry_reference + " deleted."))
