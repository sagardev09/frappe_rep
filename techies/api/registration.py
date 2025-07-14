import frappe
from frappe import _
from neonnine.neonnine.doctype.business_details.business_details import register_user
from neonnine.api.utils import exception_handler_and_logger
logger = frappe.logger("neonnine")

@frappe.whitelist(allow_guest=True)
def register_business(name=None, phone=None, address=None, email=None, business_type=None):
    try:
        logger.error(locals())
        logger.error("hey")
        # Call register_user and get the response
        result = register_user(
            name=name,
            phone=phone,
            address=address,
            email=email,
            business_type=business_type
        )
        
        # Return the response from register_user
        return result or {"status": "success", "message": "User registered successfully"}
        
    except Exception as e:
        # Make sure exception_handler_and_logger returns something
        error_response = exception_handler_and_logger(e)
        return error_response or {
            "status": "error",
            "message": str(e)
        }