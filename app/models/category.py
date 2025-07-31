"""Category model"""
from app.extensions import db


class Category(db.Model):
    """Category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(5), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Bootstrap icon class
    color = db.Column(db.String(20))  # For UI theming
    
    # Hierarchical categories
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    children = db.relationship('Category',
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    # Ordering
    sort_order = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Category {self.name} ({self.prefix})>'
    
    def get_full_path(self):
        """Get full category path (Parent > Child)"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
