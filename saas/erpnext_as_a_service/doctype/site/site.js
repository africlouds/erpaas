// Copyright (c) 2016, Africlouds Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	refresh: function(frm) {

	},
	send_confirmation_email: function(frm) {
		if (frm.doc.status==="Pending Approval"){
			frappe.call({
				method: "saas.api.send_invitation_emails",
				args: {
					site: frm.doc.name
				},
				callback: function(r){
					
				}
			})
		}
	},
	create_site: function(frm){
		frappe.call({
			method:"saas.api.create_site",
			args: {
				site: frm.doc.name
			},
			callback: function(r){
				alert(String(r))
			}
		})
	},
	delete_site: function(frm){
		frappe.call({
			method:"saas.api.delete_site",
			args: {
				site: frm.doc.name
			},
			callback: function(r){
				alert(String(r))
			}
		})
	},
});
