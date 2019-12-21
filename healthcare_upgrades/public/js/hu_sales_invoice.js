frappe.ui.form.on("Sales Invoice", {
	customer: function(frm) {
		if (frm.doc.customer) {
			frappe.db.get_value("Customer", frm.doc.customer, "hu_create_ritenuta_entry", function(r) {
				frm.set_value("hu_create_ritenuta_entry", r.hu_create_ritenuta_entry);
			})
		}
	},
	after_cancel: function(frm) {
		if(frm.doc.hu_create_ritenuta_entry) {
			frappe.msgprint(
				'<span class="bold" style="color: red">' +
				__("Please delete the journal entry for Ritenuta manually before amending the invoice.")
				+ '</span>'
			)
		}
	},
	refresh: function(frm) {
		if(!frm.doc.__islocal && frm.doc.docstatus == 0 && frm.doc.hu_create_ritenuta_entry) {
			frm.add_custom_button(__('Create Ritenuta Entry'), function () {
				frappe.call({
					method: "healthcare_upgrades.hu_sales_invoice.create_ritenuta_je_and_update_advances",
					args: {
						doc: frm.doc
					},
					freeze: true,
					freeze_message: __("Creating Ritenuta entry...")
				}).done((r) => {
					frappe.show_alert('<span class="indicator blue">' + __("Ritenuta advances updated") + '</span>')
					frappe.run_serially([
						() => frm.trigger('get_advances'),
						() => {
							frm.doc.advances.forEach((item) => {
								item.allocated_amount = item.advance_amount
							})
							if (frm.doc.hu_create_ritenuta_entry && frm.doc.advances.length > 1) {
								frappe.msgprint(
									'<span class="bold" style="color: red">' +
									__("There are multiple rows in the Advances table. Please check.")
									+ '</span>'
								)
							}
						},
						() => refresh_field("advances"),
						() => frm.save()
					]);
				})
			});
			var ritenuta_button = cur_frm.custom_buttons["Create Ritenuta Entry"];
			if (ritenuta_button) {
				ritenuta_button.removeClass("btn-default").addClass("btn-primary");
			}
		}
	}
});
