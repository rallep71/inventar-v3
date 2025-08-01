# app/utils/toast.py
"""Toast utilities for HTMX responses"""
from flask import make_response, render_template_string


def htmx_toast(response, message, category='info'):
    """Add HTMX toast trigger to response"""
    response.headers['HX-Trigger'] = f'{{"showToast": {{"message": "{message}", "category": "{category}"}}}}'
    return response


def toast_response(message, category='info', status=200):
    """Return empty response with toast trigger"""
    response = make_response('', status)
    return htmx_toast(response, message, category)


def toast_redirect(url, message, category='info'):
    """Return redirect response with toast"""
    response = make_response('', 200)
    response.headers['HX-Redirect'] = url
    return htmx_toast(response, message, category)
