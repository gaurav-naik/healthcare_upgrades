# -*- coding: utf-8 -*-
# Copyright (c) 2018, Inqubit and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class HUPhysicianSchedule(Document):
	def validate(self):
		#remove duplicates:
		unique_slots = []
		for slot in self.time_slots:
			found_slot = [us for us in unique_slots if us.date == slot.date and us.from_time == slot.from_time]
			if not found_slot:
				unique_slots.append(slot)

		if len(self.time_slots) != len(unique_slots):
			frappe.msgprint(_("Duplicate slots deleted."))

		self.time_slots = unique_slots
