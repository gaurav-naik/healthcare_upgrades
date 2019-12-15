import frappe
from frappe import _

def before_submit(doc, method):
	if doc.hu_create_ritenuta_entry:
		#create ritenuta entry and update advances
		create_ritenuta_je_and_update_advances(doc)

def on_submit(doc, method):
	if not doc.is_return:
		#create payment entry
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		new_payment_entry = get_payment_entry(doc.doctype, doc.name)
		new_payment_entry.mode_of_payment = doc.mode_of_payment
		new_payment_entry.reference_no = "-"
		new_payment_entry.reference_date = doc.posting_date or frappe.utils.getdate()
		new_payment_entry.save()
		new_payment_entry.submit()

		frappe.db.set_value("Sales Invoice", doc.name, "hu_payment_entry_reference", new_payment_entry.name)

def validate(doc, method):
	if not doc.is_return and not doc.mode_of_payment:
		frappe.throw(_("Please set Mode of Payment."))

	if not doc.is_return and doc.hu_payment_entry_reference and not frappe.db.get_value("Payment Entry", doc.hu_payment_entry_reference):
		doc.hu_payment_entry_reference = None


def on_cancel(doc, method):
	if not doc.is_return and doc.hu_payment_entry_reference:
		if frappe.db.get_value("Payment Entry", doc.hu_payment_entry_reference):
			payment_entry = frappe.get_doc("Payment Entry", doc.hu_payment_entry_reference)
			payment_entry.cancel()
			frappe.db.commit()

			frappe.delete_doc("Payment Entry", payment_entry.name)
			frappe.msgprint(_("Payment entry " + doc.hu_payment_entry_reference + " deleted."))

	#cancel_ritenuta_je(doc)

def create_ritenuta_je_and_update_advances(doc):
	# Create a journal entry to show deducted Ritenuta as an advance.
	journal_entry = frappe.new_doc("Journal Entry")
	journal_entry.voucher_type = "Journal Entry"
	journal_entry.posting_date = doc.posting_date
	journal_entry.company = doc.company

	ritenuta_account = frappe.db.get_value("EFE Settings", "EFE Settings", "ritenuta_account")

	# Ritenuta amount is 20 % of the doc amount.
	amount = doc.total * 0.2

	# Create debit and credit entries to reflect Ritenuta as an advance.
	journal_entry.append('accounts', {
		"account": ritenuta_account,
		"debit_in_account_currency": amount
	})

	debtors_account = frappe.db.get_value("Account", {"account_name": _("Debtors")}, "name")
	journal_entry.append('accounts', {
		"account": debtors_account,
		"party_type": "Customer",
		"party": doc.customer,
		"credit_in_account_currency": amount,
		"is_advance": "Yes"
	})
	journal_entry.save()
	journal_entry.submit()

	# Find the row with the debtor account in the saved journal entry for updating advances in the invoice.
	debtor_row = next((a for a in journal_entry.accounts if a.account == debtors_account), None)

	doc.append('advances', {
		"reference_name": journal_entry.name,
		"reference_row": debtor_row.name,
		"reference_type": "Journal Entry",
		"advance_amount": amount,
		"allocated_amount": amount
	})

	# Important, to re-evaluate totals.
	#doc.calculate_taxes_and_totals()

# def cancel_ritenuta_je(doc):
# 	if doc.hu_create_ritenuta_entry and len(doc.advances):
# 		for row in doc.advances:
# 			doc = frappe.get_doc(row.reference_type, row.reference_name)
# 			doc.cancel()
# 			frappe.msgprint(_("Cancelled Ritenuta Journal Entry '{0}'".format(row.reference_name)))
