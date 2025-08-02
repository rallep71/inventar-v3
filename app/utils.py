# app/utils.py
"""Utility functions for the application"""
import os
import random
import string
from datetime import datetime
from flask import request
from app.models import Item


def generate_item_id(prefix):
    """Generate unique item ID with prefix"""
    from app import db
    
    # Get current year (optional, remove if not needed)
    # year = datetime.now().strftime('%y')
    
    # Find highest number for this prefix
    last_item = Item.query.filter(
        Item.item_uid.like(f'{prefix}-%')
    ).order_by(Item.item_uid.desc()).first()
    
    if last_item:
        # Extract number from last ID
        try:
            parts = last_item.item_uid.split('-')
            last_number = int(parts[-1])
            new_number = last_number + 1
        except:
            new_number = 1
    else:
        new_number = 1
    
    # Format with leading zeros
    return f"{prefix}-{new_number:04d}"


def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def is_htmx_request():
    """Check if request is from HTMX"""
    return request.headers.get('HX-Request') == 'true'


def generate_random_string(length=8):
    """Generate random string for various purposes"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def format_currency(value):
    """Format value as currency"""
    if value is None:
        return "0,00 €"
    return f"{value:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.')


def get_file_size(file_path):
    """Get human readable file size"""
    if not os.path.exists(file_path):
        return "0 B"
    
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def sanitize_filename(filename):
    """Sanitize filename to be safe for filesystem"""
    # Remove path separators
    filename = os.path.basename(filename)
    # Remove special characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 50:
        name = name[:50]
    return name + ext
