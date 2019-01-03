frappe.ui.form.on("Customer", {
	onload: function(frm) {
		frm.set_query("hu_town", function() {
			return {
				"filters": { "is_group": 0 }
			};
		});
		frm.set_query("hu_place_of_birth", function() {
			return {
				"filters": { "is_group": 0 }
			};
		});
    },
    hu_first_name: function(frm) {
        if ("efe_first_name" in cur_frm.fields_dict) {
            frm.set_value("efe_first_name", frm.doc.hu_first_name);
        }
    },
    hu_last_name: function(frm) {
        if ("efe_last_name" in cur_frm.fields_dict) {
            frm.set_value("efe_last_name", frm.doc.hu_last_name);
        }
    },
    hu_gender: function(frm) {
        frm.set_value("gender", frm.doc.hu_gender);
    },
    hu_date_of_birth: function(frm) {
        if ("efe_date_of_birth" in cur_frm.fields_dict) {
            frm.set_value("efe_date_of_birth", frm.doc.hu_date_of_birth);
        }
    },
    hu_place_of_birth: function(frm) {
        if ("efe_place_of_birth" in cur_frm.fields_dict) {
            frm.set_value("efe_place_of_birth", frm.doc.hu_place_of_birth);
        }
    },
	hu_town: function(frm) {
        if (frm.doc.hu_town && frm.doc.hu_town.lastIndexOf("-") != -1) {
            frm.set_value("hu_pincode", frm.doc.hu_town.substr(frm.doc.hu_town.lastIndexOf("-")+1));
        }
    },
});