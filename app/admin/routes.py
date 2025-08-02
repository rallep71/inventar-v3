# Füge diese Routes zu app/admin/routes.py hinzu:

from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import or_, func
from app import db
from app.admin import admin
from app.models import Category, Item, User

# Admin-Decorator

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/')
@admin_required
def index():
    """Admin Dashboard"""
    # Hole Statistiken
    stats = {
        'total_items': Item.query.count(),
        'total_categories': Category.query.count(),
        'total_users': User.query.count(),
        'total_teams': 0  # Placeholder bis Team Model implementiert ist
    }
    
    return render_template('admin/index.html', stats=stats)

# Kategorieverwaltung Hauptseite
@admin.route('/categories')
@admin_required
def categories():
    """Kategorieverwaltung Hauptseite"""
    return render_template('admin/categories.html')

# Kategoriebaum laden
@admin.route('/categories/tree')
@admin_required
def category_tree():
    """Lade Kategoriebaum als Partial"""
    # Hole alle Root-Kategorien mit ihren Kindern
    categories = Category.query.filter_by(parent_id=None).all()
    
    # Füge Artikel-Zählung hinzu
    for category in categories:
        add_item_count(category)
    
    return render_template('admin/partials/category_tree.html', 
                         categories=categories)

# Kategorie-Statistiken
@admin.route('/categories/stats')
@admin_required
def category_stats():
    """Lade Kategorie-Statistiken"""
    total = Category.query.count()
    active = Category.query.filter_by(is_active=True).count()
    with_items = db.session.query(Category).join(Category.items).distinct().count()
    
    # Top Kategorien nach Artikelanzahl
    top_categories = db.session.query(
        Category.name,
        func.count(Item.id).label('count')
    ).join(Category.items).group_by(Category.id).order_by(
        func.count(Item.id).desc()
    ).limit(5).all()
    
    html = f"""
    <dl class="row mb-0">
        <dt class="col-sm-6">Gesamt:</dt>
        <dd class="col-sm-6">{total}</dd>
        
        <dt class="col-sm-6">Aktiv:</dt>
        <dd class="col-sm-6">{active}</dd>
        
        <dt class="col-sm-6">Mit Artikeln:</dt>
        <dd class="col-sm-6">{with_items}</dd>
    </dl>
    
    <hr>
    <h6>Top Kategorien</h6>
    <ul class="list-unstyled mb-0">
    """
    
    for cat in top_categories:
        html += f'<li>{cat.name} <span class="text-muted">({cat.count})</span></li>'
    
    html += '</ul>'
    return html

# Kategorie-Formular (Neu/Bearbeiten)
@admin.route('/categories/add')
@admin.route('/categories/<int:id>/edit')
@admin_required
def category_form(id=None):
    """Zeige Kategorie-Formular"""
    category = None
    parent = None
    
    if id:
        category = Category.query.get_or_404(id)
    
    parent_id = request.args.get('parent_id', type=int)
    if parent_id:
        parent = Category.query.get(parent_id)
    
    # Hole verfügbare Eltern-Kategorien (mit Level für Einrückung)
    available_parents = get_category_hierarchy()
    
    return render_template('admin/partials/category_form.html',
                         category=category,
                         parent=parent,
                         available_parents=available_parents)

# Kategorie speichern
@admin.route('/categories/<int:id>/save', methods=['POST'])
@admin_required
def save_category(id):
    """Speichere Kategorie (neu oder update)"""
    name = request.form.get('name', '').strip()
    prefix = request.form.get('prefix', '').strip().upper()
    parent_id = request.form.get('parent_id', type=int) or None
    description = request.form.get('description', '').strip()
    is_active = request.form.get('is_active') == '1'
    
    # Validierung
    if not name or not prefix:
        return '<div class="alert alert-danger">Name und Präfix sind erforderlich</div>', 400
    
    if not prefix.isalpha() or len(prefix) < 2 or len(prefix) > 10:
        return '<div class="alert alert-danger">Präfix muss 2-10 Großbuchstaben sein</div>', 400
    
    if id == 0:
        # Neue Kategorie
        # Prüfe ob Präfix bereits existiert
        if Category.query.filter_by(prefix=prefix).first():
            return '<div class="alert alert-danger">Präfix bereits vergeben</div>', 400
        
        category = Category(
            name=name,
            prefix=prefix,
            parent_id=parent_id,
            description=description,
            is_active=is_active
        )
        db.session.add(category)
        flash(f'Kategorie "{name}" wurde erstellt', 'success')
    else:
        # Update
        category = Category.query.get_or_404(id)
        category.name = name
        category.parent_id = parent_id
        category.description = description
        category.is_active = is_active
        
        # Präfix nur ändern wenn keine Artikel vorhanden
        if category.items.count() == 0:
            category.prefix = prefix
        
        flash(f'Kategorie "{name}" wurde aktualisiert', 'success')
    
    db.session.commit()
    
    # Gebe aktualisierten Baum zurück
    return redirect(url_for('admin.category_tree'))

# Kategorie löschen
@admin.route('/categories/<int:id>', methods=['DELETE'])
@admin_required
def delete_category(id):
    """Lösche Kategorie"""
    category = Category.query.get_or_404(id)
    
    # Prüfe ob Artikel vorhanden
    if category.items.count() > 0:
        return '<div class="alert alert-danger">Kategorie mit Artikeln kann nicht gelöscht werden</div>', 400
    
    # Prüfe ob Unterkategorien vorhanden
    if category.children:
        return '<div class="alert alert-danger">Kategorie mit Unterkategorien kann nicht gelöscht werden</div>', 400
    
    name = category.name
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Kategorie "{name}" wurde gelöscht', 'success')
    
    # Gebe aktualisierten Baum zurück
    return redirect(url_for('admin.category_tree'))

# Kategorie-Suche
@admin.route('/categories/search')
@admin_required
def search_categories():
    """Suche in Kategorien"""
    query = request.args.get('category-search', '').strip()
    
    if not query:
        return redirect(url_for('admin.category_tree'))
    
    # Suche in Name und Präfix
    categories = Category.query.filter(
        or_(
            Category.name.ilike(f'%{query}%'),
            Category.prefix.ilike(f'%{query}%')
        )
    ).all()
    
    # Baue flache Liste mit Hierarchie-Info
    result_categories = []
    for cat in categories:
        # Füge auch alle Eltern hinzu für Kontext
        add_category_with_parents(cat, result_categories)
    
    return render_template('admin/partials/category_tree.html', 
                         categories=result_categories)

# Helper-Funktionen
def add_item_count(category):
    """Füge Artikel-Zählung zu Kategorie und Kindern hinzu"""
    category.item_count = category.items.count()
    for child in category.children:
        add_item_count(child)
def get_category_hierarchy(exclude_id=None):
    """Hole alle Kategorien mit Level-Information für Einrückung"""
    categories = []
    
    def add_categories(parent_id, level):
        cats = Category.query.filter_by(parent_id=parent_id).order_by(Category.name).all()
        for cat in cats:
            if exclude_id and cat.id == exclude_id:
                continue
            # Füge level als separates Attribut hinzu (nicht das @property überschreiben)
            cat._display_level = level
            categories.append(cat)
            add_categories(cat.id, level + 1)
    
    add_categories(None, 0)
    return categories

def add_category_with_parents(category, result_list):
    """Füge Kategorie mit allen Eltern zur Liste hinzu"""
    # Implementation für Suchergebnisse mit Kontext
    parents = []
    current = category
    
    while current.parent:
        parents.append(current.parent)
        current = current.parent
    
    # Füge in umgekehrter Reihenfolge hinzu
    for parent in reversed(parents):
        if parent not in result_list:
            result_list.append(parent)
