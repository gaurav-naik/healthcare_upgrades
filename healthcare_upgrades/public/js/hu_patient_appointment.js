cur_frm.add_fetch("physician", "hu_appointment_color", "hu_appointment_color");

frappe.ui.form.on("Patient Appointment", {
	onload: function(frm) {
		//Check if patient info is filled
			
	},
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			frm.add_custom_button(__("Check Availability"), function() {
				check_physician_availability(frm);
			});
		} else {
			if (!frm.custom_buttons[__("Update Notes")]) { 
				frm.add_custom_button(__("Update Notes"), function() {
					show_update_notes_dialog(frm);
				});
			}
		}
		
		if (frm.doc.sales_invoice) {
			frm.add_custom_button(__("Delete Linked Invoice"), function() {
				frappe.call({
					method:"healthcare_upgrades.hu_patient_appointment.unlink_and_delete_sales_invoice",
					args: {
						patient_appointment: frm.doc.name
					},
					freeze: true,
					freeze_message: __("Deleting linked invoice...")
				}).done(function(r) {
					frm.reload_doc();
				}).error(function(r) {
					frappe.show_alert(__("Cannot unlink sales invoice"));
				});
			});
		}

		//Check if patient info is filled
		check_patient_details(frm);
	},
	hu_procedure: function(frm) {
		if (!frm.doc.patient) { return 0; }
		frappe.call({
			method: "healthcare_upgrades.hu_patient_appointment.get_earliest_available_physician_and_date",
		}).done(function(r) {
			if (!r.exc) {
				frm.set_value("physician", r.message.physician);
				frm.set_value("hu_appointment_color", r.message.appointment_color);
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not fetch earliest available doctor."));
		});
		check_patient_details(frm);
	},
	physician: function(frm) {
		if (!frm.doc.physician) { return 0; }
		frappe.call({
			method: "healthcare_upgrades.hu_patient_appointment.get_earliest_available_date",
			args: {
				"physician": frm.doc.physician,
			}
		}).done(function(r) {
			if(r.message) {
				frm.set_value("appointment_date", r.message);
			} else {
				frappe.show_alert(__("All slots are booked!"));
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not fetch earliest available date."));
		});
	},
	// after_save: function(frm) {
	// 	frm.reload_doc();
    // },
    
});

//CLONE Check patient availability
function check_physician_availability(frm) {
	var { physician, appointment_date } = frm.doc;
	if(!(physician && appointment_date)) {
		frappe.throw(__("Please select Physician and Date"));
	}

	// show booking modal
	frm.call({
		method: 'healthcare_upgrades.hu_patient_appointment.get_availability_data',
		args: {
			physician: physician,
			date: appointment_date
		},
		callback: (r) => {
			var data = r.message;
			if(data.available_slots.length > 0) {
				show_availability(data);
			} else {
				show_empty_state();
			}
		}
	});

	function show_empty_state() {
		frappe.msgprint({
			title: __('Not Available'),
			message: __("Physician {0} not available on {1}", [physician.bold(), appointment_date.bold()]),
			indicator: 'red'
		});
	}

	function show_availability(data) {
		// console.log("slots", data.available_slots);
		// console.log("appointments", data.appointments);
		// console.log("room_appointments", data.appointments_requiring_rooms);

		var d = new frappe.ui.Dialog({
			title: __("Available slots"),
			fields: [{ fieldtype: 'HTML', fieldname: 'available_slots'}],
			primary_action_label: __("Book"),
			primary_action: function() {
				// book slot
				frm.set_value('appointment_time', selected_slot);
				frm.set_value('duration', data.time_per_appointment * $selected_slots.length);
				d.hide();
				frm.save();
			}
		});
		var $wrapper = d.fields_dict.available_slots.$wrapper;
		var selected_slot = null;
		var $selected_slots = [];

		// disable dialog action initially
		d.get_primary_btn().attr('disabled', true);

		// make buttons for each slot
		var slot_html = data.available_slots.map(slot => {
			return `<button class="btn btn-default"
				data-name=${slot.from_time} data-room=${slot.idr_procedure_room}
				style="margin: 0 10px 10px 0; width: 72px">
				${slot.from_time.substring(0, slot.from_time.length - 3)}
			</button>`;
		}).join("");

		$wrapper
			.css('margin-bottom', 0)
			.addClass('text-center')
			.html(slot_html);

		// disable buttons for which appointments are booked
		data.appointments.map(slot => {
			if(slot.status == "Scheduled" || slot.status == "Open" || slot.status == "Closed"){
				$wrapper
					.find(`button[data-name="${slot.appointment_time}"]`)
					.attr('disabled', true)
					.addClass('btn-danger');
			}
		});

		// blue button when clicked
		$wrapper.on('click', 'button', function() {
			var $btn = $(this);

			if ($btn.hasClass('btn-primary')) {
				$btn.removeClass('btn-primary')
			} else {
				if($btn.prev().hasClass('btn-primary') || $btn.next().hasClass('btn-primary')) {
					$btn.addClass('btn-primary')
				} else {
					$wrapper.find('button').removeClass('btn-primary');
					$btn.addClass('btn-primary')
				}
			}
			$selected_slots = $wrapper.find('.btn-primary');
			selected_slot = $selected_slots.first().attr('data-name');

			// enable dialog action
			d.get_primary_btn().attr('disabled', null);
		});

		d.show();
	}
}

function check_patient_details(frm) {
	if (frm.doc.patient) {
		frappe.call({
			method: "healthcare_upgrades.hu_patient_appointment.check_patient_details",
			args: {
				patient: frm.doc.patient,
			}
		}).done(function(r) {
			if (r && r.message && r.message.missing_details && r.message.missing_details.length > 0) {
				frm.set_df_property("patient", "label", 
					__("Patient") + '<a class="badge" style="color:white;background-color:red" href="/desk#Form/Customer/' + r.message.patient_customer + '">' 
					+ __("Mancano le informazioni cliente!") + '</a>'
				);
				$("button[data-doctype='Sales Invoice'].btn-new").attr('disabled', 'disabled');

				if (cur_frm.custom_buttons["Invoice"]) {
					cur_frm.custom_buttons["Invoice"].hide();
				}
			} else {
				frm.set_df_property("patient", "label", __("Patient"));
				$("button[data-doctype='Sales Invoice'].btn-new").removeAttr('disabled');

				if (cur_frm.custom_buttons["Invoice"]) {
					cur_frm.custom_buttons["Invoice"].show();
				}
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not check patient details"));
		});
	}
}

function show_update_notes_dialog(frm) {
	var d = new frappe.ui.Dialog({
		title: __('Update Appointment Notes'),
		fields: [
			{
				"label" : "Notes",
				"fieldname": "appointment_notes",
				"fieldtype": "Text",
				"default": frm.doc.notes
			}
		],
		primary_action: function() {
			var data = d.get_values();
			frappe.call({
				method: "healthcare_upgrades.hu_patient_appointment.update_appointment_notes",
				args: {
					appointment: frm.doc.name,
					notes: data.appointment_notes || ""
				},
				callback: function(r) {
					d.hide();
					frm.reload_doc();
				}
			});
		},
		primary_action_label: __('Update')
	});
	d.show();
}
