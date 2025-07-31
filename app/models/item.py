"""Item model"""
from datetime import datetime
from app.extensions import db

# Association table for many-to-many relationship
item_categories = db.Table('item_categories',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)


class Item(db.Model):
    """Item model"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_uid = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Stock and pricing
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2))
    
    # Details
    location = db.Column(db.String(200))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    condition = db.Column(db.String(50), default='Gut')
    
    # Shipping
    weight = db.Column(db.Numeric(10, 3))  # in kg
    shipping_size = db.Column(db.String(50))
    
    # Images
    image_file = db.Column(db.String(200))
    thumbnail_file = db.Column(db.String(200))
    
    # Metadata
    barcode = db.Column(db.String(100))
    qr_code = db.Column(db.String(200))
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_sold = db.Column(db.Boolean, default=False)
    sold_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    categories = db.relationship('Category', secondary=item_categories, 
                               lazy='subquery', backref=db.backref('items', lazy=True))
    logs = db.relationship('Log', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Item {self.item_uid}: {self.name}>'
    
    def get_main_category(self):
        """Get the first category with a prefix"""
        for category in self.categories:
            if category.prefix:
                return category
        return self.categories[0] if self.categories else None
