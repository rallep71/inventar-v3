# app/models/log.py
"""Log model for activity tracking"""
from datetime import datetime
from app.extensions import db


class Log(db.Model):
    """Activity log model"""
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    
    # Log levels
    level = db.Column(db.String(20), default='info')  # info, warning, error
    
    def __repr__(self):
        return f'<Log {self.action} by User {self.user_id}>'
@property
def action_display(self):
    """Zeigt lesbare Action-Beschreibung"""
    actions = {
        'created': 'hat erstellt',
        'updated': 'hat aktualisiert',
        'deleted': 'hat gelöscht',
        'view': 'hat angesehen',
        'quantity_change': 'hat Menge geändert',
        'status_change': 'hat Status geändert'
    }
    return actions.get(self.action, self.action)
