import frappe
from frappe import _
import string
import random
from frappe.utils.background_jobs import enqueue
import subprocess

def id_generator(size=50, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
	return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def delete_account(doc, method):
	site = frappe.get_doc("Site", doc.name)
	enqueue(delete_site, site=site)

def notify_user(doc, method):
	site = frappe.get_doc("Site", doc.name)
	#site.check_permission("email")

	if site.status == "Pending Approval":
		site.email_verification_code = id_generator()
		frappe.sendmail(
			recipients = [site.email],
			sender='erp@intego.rw',
			subject="Validate your account",
			message = "Please validate your email, click on this link: https://intego.rw/api/method/saas.api.verify_account?name=%s&code=%s" % (site.name,site.email_verification_code),
			reference_doctype=site.doctype,
			reference_name=site.name
		)
		site.status = "Email Sent"
		site.save(ignore_permissions=True)
		frappe.db.commit()
		#frappe.msgprint(_("Confirmation emails sent"))
	else:
		frappe.msgprint(_("Site Status must be 'Pending Approval'"))


@frappe.whitelist(allow_guest=True)
def signup(email, domain_name, telephone="",_type='POST'):
	site = frappe.get_doc({
		"doctype": "Site",
		"title": domain_name,
		"customer_name": domain_name,
		"status": "Pending Approval",
		"email": email,
		"telephone":telephone 
	})
	site.insert(ignore_permissions=True)
	frappe.db.commit()
	return {
		"location": frappe.redirect_to_message(_('Confirm Email'),"Thank you for registering. Check your email to complete registration")
	}

@frappe.whitelist(allow_guest=True)
def verify_account(name, code):
	site = frappe.get_doc("Site", name)
	if not site:
		return {
				"location": frappe.redirect_to_message(_('Verification Error'),"<p class='text-danger'>Invalid Site Name!</p>")
			}
	if site.status != "Email Sent":
		return {
				"location": frappe.redirect_to_message(_('Verification Error'),"<p class='text-danger'>Code arlead used!</p>")
			}
	if site.email_verification_code == code:
		site.status = "Site Verified"
		site.save(ignore_permissions=True)
		frappe.db.commit()
		return  {
				"location": frappe.redirect_to_message(_('Site Verified'),"Site successfully verified! Continue to <a href='/setup?name="+site.name+"&code="+site.email_verification_code+"'><strong>Setup</strong></a>")
			} 
	else:
		return {
			"location": frappe.redirect_to_message(_('Verification Error'),"<p class='text-danger'>Invalid Code!</p>")
		}

@frappe.whitelist(allow_guest=True)
def setup_account(name, telephone, business_name, password, domain):
	site = frappe.get_doc("Site", name)
	site.business_name = business_name
	site.telephone = telephone
	site.domain = domain
	site.save(ignore_permissions=True)
	frappe.db.commit()
	enqueue(create_site, site=site, admin_password=password)
	if site.domain == "custom":
		location = "Congatulations! Your website has been setup. You will shortly receive email with login details"
	else:
		location = "Congatulations! Your website has been setup. <a href='http://"+site.title+"'>Login</a>" 
	return {
			"location": frappe.redirect_to_message(_('Website Setup'), location)
	}



def create_site(site, admin_password):
	if site.domain == "custom":
        	cmd = ["bench", "new-site", "--db-name", site.name, "--mariadb-root-username", "root", "--mariadb-root-password", 'frappe', "--admin-password", admin_password, "--install-app", "erpnext", site.title]
	else:
        	cmd = ["bench", "new-site", "--db-name", site.name, "--mariadb-root-username", "root", "--mariadb-root-password", 'frappe', "--admin-password", admin_password, "--source_sql","/home/frappe/"+site.domain+".sql",site.title]
	

        p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE,
                                            cwd="/home/frappe/frappe-bench")

        out,err = p.communicate()
	#if not err:

	# TO DO
	if True:
        	cmd = ["bench", "set-ssl-certificate", site.title, "/etc/nginx/ssl/server.crt"]
        	p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE,
                                            cwd="/home/frappe/frappe-bench")
        	out,err = p.communicate()
        	cmd = ["bench", "set-ssl-key", site.title, "/etc/nginx/ssl/server.key"]
        	p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE,
                                            cwd="/home/frappe/frappe-bench")
        	out,err = p.communicate()
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": site.title,
			"email_id": site.email,
			"status": "Lead"
		})
		# the System Manager might not have permission to create a Meeting
		lead.insert(ignore_permissions=True)
		frappe.db.commit()
		frappe.sendmail(
			recipients = [site.email],
			sender="erp@intego.rw",
			subject="Your ERP Account",
			message = "Dear Customer, your account has been create and accessible from: http://%s" % (site.title),
			reference_doctype=site.doctype,
			reference_name=site.name
		)
	

def delete_site(site):
        cmd = ["bench", "drop-site","--root-password", 'frappe', site.title]
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE,
                                            cwd="/home/frappe/frappe-bench")
        out,err = p.communicate()
	if True:
		frappe.sendmail(
			recipients = [site.email],
			sender="erp@intego.rw",
			subject="Your ERP Account Terminated",
			message = "Dear Customer, your account has been terminated",
			reference_doctype=site.doctype,
			reference_name=site.name
		)
		#lead = frappe.get_doc("Lead", site.title)
		#lead.status = "Do Not Contact"
		#lead.save(ignore_permissions=True)
		#frappe.db.commit()
	


