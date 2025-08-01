# app/main/__init__.py
"""Main blueprint for general routes"""
from flask import Blueprint

main = Blueprint('main', __name__)

from app.main import routes
