# Erweitere das Category Model in app/models/category.py:

from app import db

class Category(db.Model):
    """Category model with hierarchical structure"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    parent = db.relationship('Category', remote_side=[id], backref='children')
    items = db.relationship('Item', secondary='item_categories', back_populates='categories', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    @property
    def full_path(self):
        """Gibt den vollständigen Pfad der Kategorie zurück"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def all_parents(self):
        """Gibt alle übergeordneten Kategorien zurück"""
        parents = []
        current = self.parent
        while current:
            parents.append(current)
            current = current.parent
        return parents
    
    @property
    def all_children(self):
        """Gibt alle untergeordneten Kategorien rekursiv zurück"""
        children = []
        for child in self.children:
            children.append(child)
            children.extend(child.all_children)
        return children
    
    @property
    def level(self):
        """Gibt die Verschachtelungstiefe zurück"""
        if self.parent:
            return self.parent.level + 1
        return 0
    
    def can_delete(self):
        """Prüft ob Kategorie gelöscht werden kann"""
        return self.items.count() == 0 and len(self.children) == 0
