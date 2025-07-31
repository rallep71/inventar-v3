"""
API routes
"""
from app.api import api_bp


@api_bp.route('/status')
def status():
    return {"status": "API v1 ready"}
