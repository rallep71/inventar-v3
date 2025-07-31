from flask import Blueprint

main_bp = Blueprint('main', __name__)

# Import routes after blueprint creation
from app.main import routes
