import frappe

def exception_handler_and_logger(e):
    frappe.log_error(
        title=e.__class__.__name__,
        message=f"{frappe.get_traceback()} \n \n \n {str(e)}"
    )
    return str(e)