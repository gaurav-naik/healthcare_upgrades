frappe.ui.form.on('Patient', {
    hu_first_name: function(frm) {
        frm.trigger('set_full_name');
    },
    hu_last_name: function(frm) {
        frm.trigger('set_full_name');
    },
    hu_phone_no: function(frm) {
        frm.set_value('phone', frm.doc.hu_phone_no);
    },
    //Utility Functions.
    set_full_name: function(frm) {
        frm.set_value('patient_name', 
            [frm.doc.hu_last_name, frm.doc.hu_first_name].join(' ').trim()
        );
    },
})
