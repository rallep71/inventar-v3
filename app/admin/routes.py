from flask import render_template
from flask_login import login_required
from app.admin import admin

@admin.route("/")
@login_required
def index():
    return "<h1>Admin - Coming Soon</h1>"
