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
	site.check_permission("email")

	if site.status == "Pending Approval":
		site.email_verification_code = id_generator()
		frappe.sendmail(
			recipients = [site.email],
			sender='arwema@gmail.com',
			subject="Validate your account",
			message = "Please validate your email, click on this link: http://saas.erp:8000/api/method/saas.api.verify_account?name=%s&code=%s" % (site.name,site.email_verification_code),
			reference_doctype=site.doctype,
			reference_name=site.name
		)
		site.status = "Email Sent"
		site.save()
		frappe.msgprint(_("Confirmation emails sent"))
	else:
		frappe.msgprint(_("Site Status must be 'Pending Approval'"))


@frappe.whitelist(allow_guest=True)
def verify_account(name, code):
	site = frappe.get_doc("Site", name)
	if site.status != "Email Sent":
		return "The site does not need verification"
	if site.email_verification_code == code:
		site.status = "Site Verified"
		site.flags.ignore_permissions = True
		site.save()
		enqueue(create_site, site=site.name)
	else:
		return "Wapi"

def create_site(site):
        site = frappe.get_doc("Site", site)
        cmd = ["bench", "new-site", "--db-name", site.name, "--mariadb-root-username", "root", "--mariadb-root-password", 'frappe', "--admin-password", "logic", "--install-app", "erpnext", site.title]
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE,
                                            cwd="/home/frappe/frappe-bench")
        out,err = p.communicate()
	if not err:
		"""Create an orientation meeting when a new User is added"""
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": site.title,
			"email_id": site.email,
			"status": "Lead"
		})
		# the System Manager might not have permission to create a Meeting
		lead.flags.ignore_permissions = True
		lead.insert()
		frappe.sendmail(
			recipients = [site.email],
			sender="arwema@gmail.com",
			subject="Your ERP Account",
			message = "Dear Customer, your account has been create and accessible from: http://%s:8000" % (site.title),
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
	if not err:
		frappe.sendmail(
			recipients = [site.email],
			sender="arwema@gmail.com",
			subject="Your ERP Account Terminated",
			message = "Dear Customer, your account has been terminated",
			reference_doctype=site.doctype,
			reference_name=site.name
		)
		lead = frappe.get_doc("Lead", site.title)
		lead.flags.ignore_permissions = True
		lead.status = "Do Not Contact"
		lead.save()
	


