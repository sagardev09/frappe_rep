import frappe
from frappe import _
from frappe.utils.response import build_response

# You can add these to your app's whitelisted API methods, e.g. via hooks.py or as controller functions.

@frappe.whitelist()
def get_doc(doctype, name):
    """
    Get a single document by doctype and name.
    """
    try:
        doc = frappe.get_doc(doctype, name)
        return doc.as_dict()
    except Exception as e:
        frappe.log_error(message=str(e), title="get_doc error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}

@frappe.whitelist()
def get_doc_list(doctype, fields=None, filters=None, or_filters=None, limit_start=0, limit=20, order_by=None, group_by=None):
    """
    Get a list of documents by doctype with optional options.
    """
    try:
        res = frappe.get_list(
            doctype,
            fields=frappe.parse_json(fields) if fields else None,
            filters=frappe.parse_json(filters) if filters else None,
            or_filters=frappe.parse_json(or_filters) if or_filters else None,
            limit_start=int(limit_start),
            limit=int(limit),
            order_by=order_by,
            group_by=group_by,
            # as_dict=frappe.parse_json(as_dict) if as_dict else False
        )
        return res
    except Exception as e:
        frappe.log_error(message=str(e), title="get_doc_list error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}

@frappe.whitelist()
def get_count(doctype, filters=None, cache=False, debug=False):
    """
    Get count of documents by doctype with filters.
    """
    try:
        count = frappe.db.count(
            doctype,
            filters=frappe.parse_json(filters) if filters else None,
            cache=frappe.parse_json(cache) if isinstance(cache, str) else cache,
            debug=frappe.parse_json(debug) if isinstance(debug, str) else debug
        )
        return {"count": count}
    except Exception as e:
        frappe.log_error(message=str(e), title="get_count error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}

@frappe.whitelist()
def create_doc(doctype, data):
    """
    Create a new document.
    """
    try:
        doc = frappe.get_doc(frappe.parse_json({"doctype": doctype, **frappe.parse_json(data)}))
        doc.insert()
        frappe.db.commit()
        return doc.as_dict()
    except Exception as e:
        frappe.log_error(message=str(e), title="create_doc error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}

@frappe.whitelist()
def update_doc(doctype, name, data):
    """
    Update an existing document.
    """
    try:
        doc = frappe.get_doc(doctype, name)
        for key, value in frappe.parse_json(data).items():
            doc.set(key, value)
        doc.save()
        frappe.db.commit()
        return doc.as_dict()
    except Exception as e:
        frappe.log_error(message=str(e), title="update_doc error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}

@frappe.whitelist()
def delete_doc(doctype, name):
    """
    Delete a document.
    """
    try:
        frappe.delete_doc(doctype, name)
        frappe.db.commit()
        return {"message": "ok"}
    except Exception as e:
        frappe.log_error(message=str(e), title="delete_doc error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}

@frappe.whitelist()
def rename_doc(doctype, old_name, new_name):
    """
    Rename a document.
    """
    try:
        new_doc = frappe.rename_doc(doctype, old_name, new_name)
        frappe.db.commit()
        return {"message": f"Renamed to {new_doc}"}
    except Exception as e:
        frappe.log_error(message=str(e), title="rename_doc error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}

@frappe.whitelist()
def get_value(doctype, fieldname, filters):
    """
    Get single or multiple field values.
    fieldname can be a string or a list of strings.
    """
    try:
        value = frappe.db.get_value(
            doctype,
            frappe.parse_json(filters),
            frappe.parse_json(fieldname) if isinstance(fieldname, str) and fieldname.startswith("[") else fieldname,
            as_dict=True
        )
        return value
    except Exception as e:
        frappe.log_error(message=str(e), title="get_value error")
        frappe.local.response['http_status_code'] = 500
        return {"error": str(e)}