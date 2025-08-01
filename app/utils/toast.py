# app/utils/toast.py
import json
from flask import make_response

def htmx_toast(response, message, toast_type='info'):
    """Add toast trigger to HTMX response"""
    trigger_data = {
        'showToast': {
            'message': message,
            'type': toast_type
        }
    }
    response.headers['HX-Trigger'] = json.dumps(trigger_data)
    return response

def toast_redirect(url, message, toast_type='success'):
    """HTMX redirect with toast message"""
    response = make_response()
    response.headers['HX-Redirect'] = url
    trigger_data = {
        'showToast': {
            'message': message,
            'type': toast_type
        }
    }
    response.headers['HX-Trigger'] = json.dumps(trigger_data)
    return response

def toast_response(content, message, toast_type='info'):
    """Return content with toast message"""
    response = make_response(content)
    return htmx_toast(response, message, toast_type)
