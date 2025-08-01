# app/models/item.py
"""Item model - Erweiterte Version"""
from datetime import datetime
from app.extensions import db
from sqlalchemy import func

# Association table for many-to-many relationship
item_categories = db.Table('item_categories',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)


class Item(db.Model):
    """Item model mit allen benötigten Feldern"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_uid = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Stock and pricing
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2))
    purchase_price = db.Column(db.Numeric(10, 2))
    
    # Location
    location = db.Column(db.String(200))
    room = db.Column(db.String(100))
    shelf = db.Column(db.String(50))
    compartment = db.Column(db.String(50))
    
    # Details
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    condition = db.Column(db.String(50), default='Gut')
    
    # Shipping
    weight = db.Column(db.Numeric(10, 3))  # in kg
    dimensions = db.Column(db.String(100))  # LxWxH
    shipping_size = db.Column(db.String(50))
    
    # Images
    image_file = db.Column(db.String(200))
    thumbnail_file = db.Column(db.String(200))
    additional_images = db.Column(db.Text)  # JSON array of image paths
    
    # Metadata
    barcode = db.Column(db.String(100))
    qr_code = db.Column(db.String(200))
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_sold = db.Column(db.Boolean, default=False)
    is_borrowed = db.Column(db.Boolean, default=False)
    borrowed_to = db.Column(db.String(100))
    borrowed_date = db.Column(db.DateTime)
    sold_date = db.Column(db.DateTime)
    sold_price = db.Column(db.Numeric(10, 2))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_inventoried = db.Column(db.DateTime)
    
    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    # Relationships
    categories = db.relationship('Category', secondary=item_categories, 
                               lazy='subquery', backref=db.backref('items', lazy=True))
    logs = db.relationship('Log', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_items', foreign_keys=[created_by])
    team = db.relationship('Team', backref='items')
    
    def __repr__(self):
        return f'<Item {self.item_uid}: {self.name}>'
    
    def get_main_category(self):
        """Get the first category with a prefix"""
        for category in self.categories:
            if category.prefix:
                return category
        return self.categories[0] if self.categories else None
    
    def generate_next_uid(self):
        """Generate next UID based on category prefix"""
        category = self.get_main_category()
        if not category or not category.prefix:
            return None
            
        # Find highest number for this prefix
        prefix = category.prefix
        last_item = Item.query.filter(
            Item.item_uid.like(f'{prefix}-%')
        ).order_by(Item.item_uid.desc()).first()
        
        if last_item:
            last_number = int(last_item.item_uid.split('-')[1])
            next_number = last_number + 1
        else:
            next_number = 1
            
        return f"{prefix}-{next_number:04d}"
    
    @property
    def full_location(self):
        """Get formatted full location"""
        parts = []
        if self.room:
            parts.append(f"Raum: {self.room}")
        if self.location:
            parts.append(self.location)
        if self.shelf:
            parts.append(f"Regal: {self.shelf}")
        if self.compartment:
            parts.append(f"Fach: {self.compartment}")
        return " / ".join(parts) if parts else "Kein Standort"
    
    @property
    def status_badge(self):
        """Get status for display"""
        if self.is_sold:
            return ('danger', 'Verkauft')
        elif self.is_borrowed:
            return ('warning', 'Ausgeliehen')
        elif self.quantity <= 0:
            return ('danger', 'Nicht verfügbar')
        elif self.quantity <= 5:
            return ('warning', 'Niedriger Bestand')
        else:
            return ('success', 'Verfügbar')
    
    def to_dict(self):
        """Convert to dictionary for API"""
        return {
            'id': self.id,
            'uid': self.item_uid,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else None,
            'location': self.full_location,
            'categories': [cat.name for cat in self.categories],
            'status': self.status_badge[1],
            'image': self.image_file,
            'created_at': self.created_at.isoformat()
        }
