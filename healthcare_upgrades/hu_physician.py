import frappe

def validate(doc, method):
    if doc.hu_physician_schedule and not doc.physician_schedule:
		if not frappe.db.exists("Physician Schedule", doc.hu_physician_schedule):
			dummy_schedule = frappe.new_doc("Physician Schedule")
			dummy_schedule.schedule_name = doc.hu_physician_schedule
			dummy_schedule.save(ignore_permissions=True)
		doc.db_set("physician_schedule", doc.hu_physician_schedule)
		doc.db_set("time_per_appointment", 20)
		frappe.db.commit()
