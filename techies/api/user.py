import frappe
from frappe.exceptions import DoesNotExistError
@frappe.whitelist()
def check_login():
    return frappe.session.user

@frappe.whitelist()
def get_user(user = None):
	# user = frappe.session.user
	if not user:
		user = frappe.session.user
	# user="mohammed@mugen.ae"
	roles = frappe.get_roles(user)
	doc = frappe.get_doc("User", user)
	user_type = doc.user_type
	user_image = doc.user_image
	emp_id = None
	full_name = doc.full_name
	primary_language = doc.language
	timezone = doc.time_zone
	role_profile = doc.role_profile_name
	if frappe.db.exists("Employee", {"user_id": user}):
		emp_id = frappe.get_cached_value("Employee", {"user_id": user}, "name")
	res = {}
	print(emp_id)
	
	res["user"] = user
	res["roles"] = roles
	res["user_type"] = user_type
	res["user_image"] = user_image
	res["full_name"] = full_name
	res["primary_language"] = primary_language
	res["timezone"] = timezone
	res["role_profile"] = role_profile
	if emp_id:
		res["emp_id"] = emp_id 
	
	# print(res)
	return res
		
# def test():
#     get_user_and_role("dev@mugen.ae")

