frappe.views.calendar["Patient Appointment"] = {
	field_map: {
		"allDay": "allDay",
	},
	gantt: false,
	get_events_method: "healthcare_upgrades.hu_patient_appointment.get_events"
}