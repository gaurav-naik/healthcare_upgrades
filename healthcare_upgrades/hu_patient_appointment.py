import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.utils.html_utils import sanitize_html

#For Create Sales Invoice Override 
from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
from erpnext.healthcare.doctype.patient_appointment.patient_appointment import get_fee_validity
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_receivable_account,get_income_account


def on_update(doc, method):
    appointment_description = generate_appointment_description(doc)
    frappe.db.set_value("Patient Appointment", doc.name, "hu_appointment_description", appointment_description)
    frappe.db.commit()


@frappe.whitelist()
def get_earliest_available_date(physician):
    #Get dates for today's timeslots and future timeslots.
    all_slot_dates = frappe.get_all("HU Physician Schedule Time Slot", fields=["date"], distinct=True, 
        order_by="date", filters={"parent": physician, "date": (">=", frappe.utils.getdate())})
    all_slot_dates = [slot.date for slot in all_slot_dates]

    #Compare timeslots and appointments on each date.
    for date in all_slot_dates:
        timeslots = frappe.get_all("HU Physician Schedule Time Slot", 
            filters={ "date":date, "parent":physician },
            fields=["date AS date", "from_time AS time"]
        )

        appointments = frappe.get_all("Patient Appointment",
            filters={ "appointment_date": date, "physician":physician },
            fields=["appointment_date AS date", "appointment_time as time"]
        )
        
        available_slots = [timeslot for timeslot in timeslots if timeslot not in appointments]
        #Return the date if there are available slots on this date.
        if len(available_slots):
            return date

    #If the loop has completed, it implies that there are no free slots in the schedule.
    return None

@frappe.whitelist()
def get_earliest_available_physician_and_date():
    physician = frappe.db.get_value("HU Settings", "HU Settings", "default_physician")
    return {
        "physician": physician,
        "appointment_color": frappe.db.get_value("Physician", physician, "hu_appointment_color"),
        "earliest_available_date": get_earliest_available_date(physician)
    }

@frappe.whitelist()
def get_availability_data(date, physician):
	"""
	Get availability data of 'physician' on 'date'
	:param date: Date to check in schedule
	:param physician: Name of the physician
	:return: dict containing a list of available slots, list of appointments and time of appointments
	"""
	date = frappe.utils.getdate(date)
	weekday = date.strftime("%A")

	available_slots = []
	physician_schedule_name = None
	physician_schedule = None
	time_per_appointment = 0
	

	# get physicians schedule
	physician_schedule_name = frappe.db.get_value("Physician", physician, "hu_physician_schedule")
	if physician_schedule_name:
		physician_schedule = frappe.get_doc("HU Physician Schedule", physician_schedule_name)
		time_per_appointment = int(frappe.db.get_value("Physician", physician, "time_per_appointment") or 0)
	else:
		frappe.throw(_("Dr {0} does not have a Physician Schedule. Add it in Physician master".format(physician)))

	is_on_holiday = False
	if physician_schedule:
		for t in physician_schedule.time_slots:
			if date == t.date:
				if frappe.db.get_value("Holiday", {"holiday_date": date}):
					is_on_holiday = True
				else:
					available_slots.append(t)
			
	# `time_per_appointment` should never be None since validation in `Patient` is supposed to prevent
	# that. However, it isn't impossible so we'll prepare for that.
	if not time_per_appointment:
		frappe.throw(_('"Time Per Appointment" hasn"t been set for Dr {0}. Add it in Physician master.').format(physician))

	if is_on_holiday:
		frappe.throw(_("Physician is on holiday on {0}").format(weekday))

	# if physician not available return
	if not available_slots:
		# TODO: return available slots in nearby dates
		frappe.throw(_("Physician not available on {0}").format(weekday))

	# if physician on leave return

	# if holiday return
	# if is_holiday(weekday):

	# get appointments on that day for physician
	appointments = frappe.get_all(
		"Patient Appointment",
		filters={"physician": physician, "appointment_date": date},
		fields=["name", "appointment_time", "duration", "status"])
	
	#190127: Postprocess appointments: If appointment duration exceeds physician's time per appointment, add dummy appointments in 
	# data, so that they appear as booked slots.
	ghost_appointments = [] #Additional appointment slots which represent an actual appointment
	for appointment in appointments:
		print(appointment.name, appointment.duration, time_per_appointment, appointment.appointment_time, appointment.against)
		if appointment.duration > time_per_appointment:
			start_time = appointment.appointment_time + frappe.utils.datetime.timedelta(minutes=time_per_appointment)
			for x in xrange(1, appointment.duration/time_per_appointment): #For a 60 minute appointment at 11:00, this loop will add two slots: 11:20, 11:40
				ghost_slot = frappe._dict(appointment_time=start_time, duration=time_per_appointment, status="Scheduled", against=appointment.name)
				ghost_appointments.append(ghost_slot)
				start_time += frappe.utils.datetime.timedelta(minutes=time_per_appointment)
			appointments += ghost_appointments

	return {
		"available_slots": available_slots,
		"appointments": appointments,
		"time_per_appointment": time_per_appointment
	}

@frappe.whitelist()
def get_events(start, end, filters=None):
    from frappe.desk.calendar import get_event_conditions
    conditions = get_event_conditions("Patient Appointment", filters)
    data = frappe.db.sql("""select name, patient, physician, status, hu_appointment_description as 'title', 
		duration, timestamp(appointment_date, appointment_time) as
		'start', hu_appointment_color as 'color' from `tabPatient Appointment` where
		(appointment_date between %(start)s and %(end)s)
		and docstatus < 2 {conditions}""".format(conditions=conditions),
		{"start": start, "end": end}, as_dict=True, update={"allDay": 0})
    for item in data:
		item.end = item.start + frappe.utils.datetime.timedelta(minutes = int(item.duration))
    
    return data

@frappe.whitelist()
def check_patient_details(patient):
	#Check if Customer has First Name, Last Name, Place of Birth, Tax ID, Phone Number (Contact)
	out = frappe._dict(patient_customer=None, missing_details=[])

	patient_customer = frappe.db.get_value("Patient", patient, "customer")
	if not patient_customer:
		frappe.throw(_("Patient {0} does not have a linked customer.").format(patient))
		out.missing_details.append(_("Customer"))
		return out

	out.patient_customer = patient_customer
	customer = frappe.get_doc("Customer", patient_customer)

	#Get existing address. Return 0 if not found.
	existing_address_name = get_default_address("Customer", patient_customer)

	if not existing_address_name:
		out.missing_details.append(_("Address"))
		return out

	existing_address = frappe.get_doc("Address",existing_address_name) 

	if not customer.tax_id:
		out.missing_details.append(_("Tax ID"))

	if not existing_address.address_line1:
		out.missing_details.append(_("Address Line 1"))

	if not existing_address.city:
		out.missing_details.append(_("City"))

	if not existing_address.pincode:
		out.missing_details.append(_("Pincode"))

	return out

@frappe.whitelist()
def update_appointment_notes(appointment, notes):
	# notes = sanitize_html(notes)
	frappe.db.set_value("Patient Appointment", appointment, "notes", notes)

@frappe.whitelist()
def unlink_and_delete_sales_invoice(patient_appointment):
	sales_invoice = frappe.get_doc("Sales Invoice", {"appointment": patient_appointment})
	if sales_invoice.docstatus == 1:
		frappe.throw(_("Cannot delete a submitted Sales Invoice"))
	fee_validity_name = frappe.db.get_value("Fee Validity", {"ref_invoice": sales_invoice.name})

	try:
		frappe.db.set_value("Sales Invoice", sales_invoice.name, "appointment", None)
		frappe.db.set_value("Patient Appointment", patient_appointment, "sales_invoice", None)
		frappe.db.set_value("Fee Validity", fee_validity_name, "ref_invoice", None)
	except Exception as e:
		raise
	#Delete doc
	frappe.delete_doc("Sales Invoice", sales_invoice.name)
	frappe.db.commit()

@frappe.whitelist()
def create_invoice(company, physician, patient, appointment_id, appointment_date):
	if not appointment_id:
		return False
	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.customer = frappe.get_value("Patient", patient, "customer")
	sales_invoice.tax_id = frappe.get_value("Customer", sales_invoice.customer, "tax_id")
	sales_invoice.appointment = appointment_id
	sales_invoice.hu_physician = frappe.db.get_value("Patient Appointment", appointment_id, "physician")
	sales_invoice.due_date = frappe.utils.getdate()
	sales_invoice.is_pos = '0'
	sales_invoice.debit_to = get_receivable_account(company)
	sales_invoice.mode_of_payment =  frappe.db.get_value("HU Settings", "HU Settings", "default_mode_of_payment")
	appointment = frappe.get_doc("Patient Appointment", appointment_id)

	default_selling_price_list = frappe.db.get_value("IDR Settings", "IDR Settings", "default_selling_price_list")
	rate = frappe.db.get_value("Item Price", {"item_code":appointment.hu_procedure, "price_list":default_selling_price_list}, "price_list_rate")
	sales_invoice.append("items", {
	    "item_code": appointment.hu_procedure,
	    "description":  frappe.db.get_value("Item", appointment.hu_procedure, "description"),
	    "qty": 1,
	    "uom": "Nos",
	    "conversion_factor": 1,
	    "income_account": get_income_account(physician, company),
	    "rate": rate, 
	    "amount": rate,
	    "item_group": frappe.db.get_value("Item", {"item_code":appointment.hu_procedure}, "item_group")
	})

	taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=company)
	if taxes.get('taxes'):
		sales_invoice.update(taxes)

	sales_invoice.save(ignore_permissions=True)

	fee_validity = get_fee_validity(physician, patient, appointment_date)

	frappe.db.sql("""update `tabPatient Appointment` set sales_invoice=%s where name=%s""", (sales_invoice.name, appointment_id))
	frappe.db.set_value("Fee Validity", fee_validity.name, "ref_invoice", sales_invoice.name)
	consultation = frappe.db.exists({
			"doctype": "Consultation",
			"appointment": appointment_id})
	if consultation:
		frappe.db.set_value("Consultation", consultation[0][0], "invoice", sales_invoice.name)

	return sales_invoice.name

def generate_appointment_description(doc):
	return frappe.db.get_value("Patient", doc.patient, "hu_last_name") + " " + \
		frappe.db.get_value("Patient", doc.patient, "hu_first_name")[0].upper() + ". " + \
		frappe.db.get_value("Physician", doc.physician, "last_name")[0].upper() + \
		frappe.db.get_value("Physician", doc.physician, "first_name")[0].upper()

