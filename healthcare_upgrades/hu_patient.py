import frappe
from frappe.contacts.doctype.contact.contact import get_default_contact

def on_update(doc, method):
    if doc.customer and frappe.db.exists("Customer", doc.customer):
        customer = frappe.get_doc("Customer", doc.customer)
        customer.customer_name = doc.patient_name
        customer.gender = doc.sex
        customer.save()
        frappe.db.commit()
        
        default_contact_name = get_default_contact("Customer", doc.customer)

        contact = None
        if default_contact_name:
            contact = frappe.get_doc("Contact", default_contact_name)
        else:
            contact = frappe.new_doc("Contact")
            contact.append('links', { "link_doctype": "Customer", "link_name": doc.customer })
    
        contact.first_name = doc.hu_first_name
        contact.last_name = doc.hu_last_name
        contact.phone = doc.phone
    
        contact.save(ignore_permissions=True)
