from flask import render_template
from flask_login import login_required
from app.items import items

@items.route("/")
@login_required
def index():
    return "<h1>Items - Coming Soon</h1>"
