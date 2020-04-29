// Copyright (c) 2018, Inqubit and contributors
// For license information, please see license.txt

frappe.ui.form.on('HU Physician Schedule', {
	refresh: function(frm) {
		frm.add_custom_button(__('Add Time Slots by Date'), () => {
			var d = new frappe.ui.Dialog({
				fields: [
					{fieldname: 'from_date', label: __('From Date'), fieldtype:'Date'},
					{fieldname: 'cb0', fieldtype:"Column Break"},
					{fieldname: 'to_date', label: __('To Date'), fieldtype:'Date'},
					{fieldname: 'sb1', fieldtype:"Section Break"},
					{fieldname: 'monday', label: __("Monday"), fieldtype:"Check", default:1},
					{fieldname: 'tuesday', label: __("Tuesday"), fieldtype:"Check"},
					{fieldname: 'wednesday', label: __("Wednesday"), fieldtype:"Check"},
					{fieldname: 'cb1', fieldtype:"Column Break"},
					{fieldname: 'thursday', label: __("Thursday"), fieldtype:"Check"},
					{fieldname: 'friday', label: __("Friday"), fieldtype:"Check"},
					{fieldname: 'saturday', label: __("Saturday"), fieldtype:"Check"},
					{fieldname: 'sb2', fieldtype:"Section Break"},
					{fieldname: 'from_time', label:__('From'), fieldtype:'Time',
						'default': '09:00:00', reqd: 1},
					{fieldname: 'to_time', label:__('To'), fieldtype:'Time',
						'default': '12:00:00', reqd: 1},
					{fieldname: 'duration', label:__('Appointment Duration (mins)'),
						fieldtype:'Int', 'default': 20, reqd: 1},
				],
				primary_action_label: __('Add Timeslots'),
				primary_action: () => {
					var values = d.get_values();
					if(values) {
						var day_values = [
							{"day":"Monday", "checked":values.monday, "dow":1},
							{"day":"Tuesday", "checked":values.tuesday,"dow":2},
							{"day":"Wednesday","checked": values.wednesday, "dow":3},
							{"day":"Thursday","checked": values.thursday, "dow":4},
							{"day":"Friday","checked": values.friday, "dow":5},
							{"day":"Saturday","checked": values.saturday, "dow":6}
						];

						var selected_days = day_values.filter(function(day) { return day.checked == 1 });
						var selected_days_dow=[];

						selected_days.forEach(function(selected_day){
							selected_days_dow.push(selected_day.dow);
						});

						var getDates = function(startDate, endDate) {
							startDate = new Date(startDate);
							endDate = new Date(endDate);

							var dates = [],
								currentDate = startDate,
								addDays = function(days) {
									var date = new Date(this.valueOf());
									date.setDate(date.getDate() + days);
									return date;
								};
							while (currentDate <= endDate) {
								if(selected_days_dow.indexOf(currentDate.getDay()) != -1) {
									dates.push(currentDate);
								}
								currentDate = addDays.call(currentDate, 1);
							}
							return dates;
						};

						// Usage
						var dates = getDates(values.from_date, values.to_date);
						dates.forEach(function(date) {
							let cur_time = moment(values.from_time, 'HH:mm:ss');
							let end_time = moment(values.to_time, 'HH:mm:ss');

							while(cur_time < end_time) {
								let to_time = cur_time.clone().add(values.duration, 'minutes');
								if(to_time <= end_time) {
									let time_slot = {
										from_time: cur_time.format('HH:mm:ss'),
										to_time: to_time.format('HH:mm:ss'),
										date: date.toISOString().split('T')[0]
									}
									// add a new timeslot
									frm.add_child('time_slots', time_slot);

								}
								cur_time = to_time;
							}
						});

						frm.refresh_field('time_slots');
						frappe.show_alert({
							message:__('Time slots added'),
							indicator:'green'
						});
					}
				},
			});
			d.show();
		});

		frm.add_custom_button(__("Delete all Slots"), function(){
			frappe.confirm(__('Delete all slots?'),
			    function(){
			        frm.clear_table("time_slots");
					refresh_field("time_slots");
			    },
			    function(){}
			);
		});
	}
});
