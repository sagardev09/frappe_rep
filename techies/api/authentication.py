from __future__ import unicode_literals

import frappe

from frappe.utils import cint
from techies.api.auth import get_bearer_token

from techies.api.auth_api import get_user

from frappe import _


logger=frappe.logger("realjwt", file_count=1)
def test():
	a=get_bearer_token("Administrator")
	print(a)
	# logger.error("test")
def on_session_creation(login_manager=None):
	logger.error(f"vig On session creation is being called {frappe.form_dict}\n")
	# import frappe
	# logger.error("Ethi")
	# from newui.api.utils.auth import get_bearer_token
	use_jwt=0
	if frappe.form_dict.get('use_jwt') and cint(frappe.form_dict.get('use_jwt')):
		use_jwt=1
	if frappe.form_dict.get('tmp_id'):
		use_jwt = 1
	if use_jwt:
		expires_in = 604800
		frappe.local.response['token'] = get_bearer_token(
			user=login_manager.user, expires_in=expires_in
		)["access_token"]
		userdata=get_user()
		frappe.local.response['userdata'] = userdata
		frappe.flags.jwt_clear_cookies = True
  
	# get_party(login_manager.user)

@frappe.whitelist(allow_guest=True)
def clear_cookies1():
    """
    API to clear specified cookies when the endpoint is hit.
    """
    try:
        # Clear the specified cookies
        frappe.local.response["cookie"] = {
            "user_image": "",
            "system_user": "",
            "full_name": "",
            "user_id": "",
            "sid": "",
        }

        # Set expiration date to a past date for clearing the cookies
        frappe.local.response["headers"] = {
            "Set-Cookie": [
                "user_image=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/;",
                "system_user=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/;",
                "full_name=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/;",
                "user_id=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/;",
                "sid=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/;",
            ]
        }

        return {"status": "success", "message": _("Cookies cleared successfully.")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error in clearing cookies"))
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_logged_user():
	user = frappe.session.user
 

@frappe.whitelist()
def clear_cookies():
	if hasattr(frappe.local, "session"):
		frappe.session.sid = ""
	frappe.local.cookie_manager.delete_cookie(["full_name", "user_id", "sid", "user_image", "system_user"])