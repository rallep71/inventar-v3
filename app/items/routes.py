# app/items/routes.py - Add these routes to your existing routes.py

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_  # Neu hinzufügen!
import os
from datetime import datetime
from app import db
from app.items import items
from app.models import Item, Category, Log, User  # Nur einmal
from app.config import Config

# Add these helper functions at the top

# Helper functions

# Helper functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_item_id(category_prefix):
    """Generate next item ID for a category"""
    last_item = Item.query.filter(
        Item.item_uid.like(f'{category_prefix}-%')
    ).order_by(Item.item_uid.desc()).first()
    
    if last_item:
        last_num = int(last_item.item_uid.split('-')[1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{category_prefix}-{new_num:04d}"

# Main index route - THIS WAS MISSING!
@items.route("/")
@login_required
def index():
    """Items list with search, filter and pagination"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category', type=int)
    location = request.args.get('location', '').strip()
    status = request.args.get('status', '').strip()
    sort = request.args.get('sort', 'newest')
    
    # Build query
    query = Item.query
    
    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Item.name.ilike(search_filter),
                Item.item_uid.ilike(search_filter),
                Item.brand.ilike(search_filter),
                Item.model.ilike(search_filter),
                Item.description.ilike(search_filter),
                Item.serial_number.ilike(search_filter)
            )
        )
    
    # Apply category filter
    if category_id:
        query = query.join(Item.categories).filter(Category.id == category_id)
    
    # Apply location filter
    if location:
        query = query.filter(Item.location == location)
    
    # Apply status filter
    if status:
        query = query.filter(Item.status == status)
    
    # Apply team filter for non-admins
    if not current_user.is_admin():
        team_ids = [team.id for team in current_user.teams]
        if team_ids:
            query = query.filter(Item.team_id.in_(team_ids))
    
    # Apply sorting
    if sort == 'newest':
        query = query.order_by(Item.created_at.desc())
    elif sort == 'oldest':
        query = query.order_by(Item.created_at.asc())
    elif sort == 'name':
        query = query.order_by(Item.name.asc())
    elif sort == 'quantity_high':
        query = query.order_by(Item.quantity.desc())
    elif sort == 'quantity_low':
        query = query.order_by(Item.quantity.asc())
    else:
        query = query.order_by(Item.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(
        page=page,
        per_page=Config.ITEMS_PER_PAGE,
        error_out=False
    )
    
    # Get categories for filter dropdown
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    
    # Get unique locations for filter
    locations = db.session.query(Item.location).distinct().filter(
        Item.location.isnot(None),
        Item.location != ''
    ).order_by(Item.location).all()
    locations = [loc[0] for loc in locations]
    
    # Check if this is an HTMX request
    if request.headers.get('HX-Request'):
        # Return only the items grid partial
        return render_template('items/partials/items_grid.html',
                             items=pagination.items,
                             pagination=pagination,
                             search=search,
                             category_id=category_id,
                             location=location,
                             status=status,
                             sort=sort)
    
    # Return full page
    return render_template('items/index.html',
                         items=pagination.items,
                         pagination=pagination,
                         categories=categories,
                         locations=locations,
                         search=search,
                         category_id=category_id,
                         location=location,
                         status=status,
                         sort=sort)

# Detail view route
@items.route("/<int:id>")
@login_required
def detail(id):
    """Item detail view"""
    item = Item.query.get_or_404(id)
    
    # Check access rights
    if not current_user.is_admin():
        team_ids = [team.id for team in current_user.teams]
        if item.team_id and item.team_id not in team_ids:
            flash('Sie haben keine Berechtigung, diesen Artikel anzuzeigen.', 'error')
            return redirect(url_for('items.index'))
    
    # Log view action
    log = Log(
        user_id=current_user.id,
        item_id=item.id,
        action='view',
        details=f'Artikel {item.item_uid} angezeigt'
    )
    db.session.add(log)
    db.session.commit()
    
    # Get recent logs
    recent_logs = Log.query.filter_by(item_id=item.id)\
                          .order_by(Log.timestamp.desc())\
                          .limit(10).all()
    
    # Get creator info
    creator = User.query.get(item.created_by) if item.created_by else None
    
    return render_template('items/detail.html', 
                         item=item,
                         recent_logs=recent_logs,
                         creator=creator)

# Scan route
@items.route("/scan")
@login_required
def scan():
    """QR code scanner page"""
    return render_template('items/scan.html')

# Add Item Routes

# Fixed add route for app/items/routes.py

# EINFACHE VERSION DER add() FUNKTION
# Kopiere diese komplette Funktion in deine app/items/routes.py

@items.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    """Add new item with image upload"""
    if request.method == 'GET':
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        return render_template('items/add.html', categories=categories)
    
    # POST - Create new item
    name = request.form.get('name', '').strip()
    quantity = int(request.form.get('quantity', 1))
    category_id = request.form.get('category_ids')
    
    if not name or not category_id:
        flash('Name und Kategorie sind erforderlich', 'error')
        return redirect(url_for('items.add'))
    
    category = Category.query.get(category_id)
    if not category:
        flash('Ungültige Kategorie', 'error')
        return redirect(url_for('items.add'))
    
    # Generate item ID
    from app.utils import generate_item_id
    item_uid = generate_item_id(category.prefix)
    
    # Create item
    item = Item(
        item_uid=item_uid,
        name=name,
        quantity=quantity,
        brand=request.form.get('brand', ''),
        location=request.form.get('location', ''),
        notes=request.form.get('notes', ''),
        created_by=current_user.id
    )
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # Secure the filename
            filename = secure_filename(file.filename)
            # Add timestamp to make unique
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            name_part = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            filename = f"{name_part}_{timestamp}{ext}"
            
            # Save file
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            item.image_file = filename
    
    # Add category
    item.categories.append(category)
    
    try:
        db.session.add(item)
        db.session.commit()
        
        # Log creation
        log = Log(
            user_id=current_user.id,
            item_id=item.id,
            action='create',
            details=f'Artikel {item.item_uid} erstellt'
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Artikel {item.name} wurde erfolgreich erstellt!', 'success')
        return redirect(url_for('items.detail', id=item.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating item: {str(e)}')
        flash('Fehler beim Erstellen des Artikels', 'error')
        return redirect(url_for('items.add'))


@items.route("/check_duplicate")
@login_required
def check_duplicate():
    """Check if item name already exists (HTMX endpoint)"""
    name = request.args.get('name', '').strip()
    
    if not name:
        return ""
    
    existing = Item.query.filter_by(name=name).first()
    
    if existing:
        return '<span class="text-warning"><i class="bi bi-exclamation-triangle"></i> Ein Artikel mit diesem Namen existiert bereits</span>'
    
    return '<span class="text-success"><i class="bi bi-check-circle"></i> Name ist verfügbar</span>'

@items.route("/preview_id", methods=['POST'])
@login_required
def preview_id():
    """Preview generated item ID based on selected categories (HTMX endpoint)"""
    category_ids = request.form.getlist('category_ids')
    
    if not category_ids:
        return '''<div class="alert alert-info">
            <i class="bi bi-info-circle"></i> 
            Wählen Sie eine Kategorie aus, um die Artikel-ID zu generieren
        </div>'''
    
    # Get first category
    category = Category.query.get(category_ids[0])
    if not category:
        return '<div class="alert alert-warning">Ungültige Kategorie</div>'
    
    # Generate preview ID
    next_id = generate_item_id(category.prefix)
    
    return f'''<div class="alert alert-success">
        <i class="bi bi-check-circle"></i> 
        Artikel-ID wird sein: <strong>{next_id}</strong>
        <small class="text-muted">(Kategorie: {category.name})</small>
    </div>'''

@items.route("/upload_preview", methods=['POST'])
@login_required
def upload_preview():
    """Preview uploaded image (HTMX endpoint)"""
    if 'image' not in request.files:
        return ""
    
    file = request.files['image']
    if not file or not file.filename:
        return ""
    
    if not allowed_file(file.filename):
        return '<div class="alert alert-danger">Ungültiges Dateiformat. Erlaubt: JPG, PNG, WebP</div>'
    
    # For preview, we'll just show the filename
    # In production, you might want to actually save a temp file
    return f'''<div class="alert alert-info">
        <i class="bi bi-image"></i> Bild ausgewählt: {secure_filename(file.filename)}
    </div>'''
# Add these routes to your app/items/routes.py file

# Fixed edit route for app/items/routes.py

@items.route("/<int:id>/edit", methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit item with image upload"""
    item = Item.query.get_or_404(id)
    
    if not current_user.is_admin() and item.created_by != current_user.id:
        flash('Sie können nur Ihre eigenen Artikel bearbeiten.', 'error')
        return redirect(url_for('items.detail', id=item.id))
    
    if request.method == 'GET':
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        return render_template('items/edit.html', item=item, categories=categories)
    
    # POST - Update item
    item.name = request.form.get('name', item.name)
    item.quantity = int(request.form.get('quantity', item.quantity))
    item.brand = request.form.get('brand', '')
    item.location = request.form.get('location', '')
    item.notes = request.form.get('notes', '')
    
    # Update category
    category_id = request.form.get('category_ids')
    if category_id:
        category = Category.query.get(category_id)
        if category:
            item.categories = [category]
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # Delete old image if exists
            if item.image_file:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_file)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Save new image
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            name_part = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            filename = f"{name_part}_{timestamp}{ext}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            item.image_file = filename
    
    try:
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log update
        log = Log(
            user_id=current_user.id,
            item_id=item.id,
            action='update',
            details=f'Artikel {item.item_uid} aktualisiert'
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Artikel wurde erfolgreich aktualisiert!', 'success')
        return redirect(url_for('items.detail', id=item.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating item: {str(e)}')
        flash('Fehler beim Aktualisieren des Artikels', 'error')
        return redirect(url_for('items.edit', id=item.id))


@items.route("/<int:id>/delete", methods=['POST'])
@login_required
def delete(id):
    """Delete item - POST only"""
    item = Item.query.get_or_404(id)
    
    if not current_user.is_admin() and item.created_by != current_user.id:
        flash('Sie können nur Ihre eigenen Artikel löschen.', 'error')
        return redirect(url_for('items.index'))
    
    # Delete image if exists
    if item.image_file:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_file)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
    
    # Log deletion before deleting item
    log = Log(
        user_id=current_user.id,
        action='delete',
        details=f'Artikel {item.item_uid} - {item.name} gelöscht'
    )
    
    try:
        db.session.add(log)
        db.session.delete(item)
        db.session.commit()
        
        flash('Artikel wurde erfolgreich gelöscht!', 'success')
        return redirect(url_for('items.index'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting item: {str(e)}')
        flash('Fehler beim Löschen des Artikels', 'error')
        return redirect(url_for('items.detail', id=item.id))


@items.route("/<int:id>/quick_update", methods=['POST'])
@login_required
def quick_update(id):
    """Quick update for quantity (HTMX endpoint)"""
    item = Item.query.get_or_404(id)
    action = request.form.get('action')
    
    if action == 'increment':
        item.quantity += 1
    elif action == 'decrement' and item.quantity > 0:
        item.quantity -= 1
    
    db.session.commit()
    
    # Return updated quantity badge
    return f'<span id="quantity-{item.id}" class="btn btn-outline-secondary disabled">{item.quantity}</span>'
# Add these routes to your app/items/routes.py file

@items.route("/search/<item_uid>")
@login_required
def search_by_uid(item_uid):
    """Search and redirect to item by UID"""
    item = Item.query.filter_by(item_uid=item_uid).first()
    
    if item:
        # Check access rights
        if not current_user.is_admin():
            team_ids = [team.id for team in current_user.teams]
            if item.team_id and item.team_id not in team_ids:
                flash('Sie haben keine Berechtigung, diesen Artikel anzuzeigen.', 'error')
                return redirect(url_for('items.index'))
        
        return redirect(url_for('items.detail', id=item.id))
    else:
        flash(f'Artikel mit ID {item_uid} nicht gefunden.', 'warning')
        return redirect(url_for('items.scan'))

@items.route("/search_by_id")
@login_required
def search_by_id():
    """AJAX search by item ID (for manual input)"""
    item_uid = request.args.get('item_uid', '').strip().upper()
    
    if not item_uid:
        return '<div class="alert alert-warning">Bitte geben Sie eine Artikel-ID ein.</div>'
    
    item = Item.query.filter_by(item_uid=item_uid).first()
    
    if item:
        # Check access rights
        if not current_user.is_admin():
            team_ids = [team.id for team in current_user.teams]
            if item.team_id and item.team_id not in team_ids:
                return '<div class="alert alert-danger">Keine Berechtigung für diesen Artikel.</div>'
        
        # Return item card
        return f'''
        <div class="card mt-3">
            <div class="card-body">
                <h5 class="card-title">{item.name}</h5>
                <p class="card-text">
                    <strong>ID:</strong> {item.item_uid}<br>
                    <strong>Marke:</strong> {item.brand or '-'}<br>
                    <strong>Bestand:</strong> {item.quantity}<br>
                    <strong>Standort:</strong> {item.location or '-'}
                </p>
                <a href="{url_for('items.detail', id=item.id)}" class="btn btn-primary">
                    <i class="bi bi-eye"></i> Details anzeigen
                </a>
            </div>
        </div>
        '''
    else:
        return f'<div class="alert alert-warning">Kein Artikel mit der ID <strong>{item_uid}</strong> gefunden.</div>'

# Füge diese Route zu app/items/routes.py hinzu:

@items.route("/<int:id>/history")
@login_required
def history(id):
    """Get item history for HTMX request"""
    item = Item.query.get_or_404(id)
    
    # Check permissions
    if not current_user.is_admin() and item.team_id != current_user.team_id:
        abort(403)
    
    logs = Log.query.filter_by(item_id=id)\
                    .order_by(Log.timestamp.desc())\
                    .limit(20).all()
    
    # Return partial template
    return render_template('items/partials/history.html', logs=logs)

@items.route("/<int:id>/duplicate", methods=['POST'])
@login_required
def duplicate(id):
    """Duplicate an item"""
    item = Item.query.get_or_404(id)
    
    # Check permissions
    if not current_user.is_admin() and item.team_id != current_user.team_id:
        abort(403)
    
    # Create duplicate
    new_item = Item(
        item_uid=generate_item_id(item.categories[0].prefix if item.categories else 'MISC'),
        name=f"{item.name} (Kopie)",
        description=item.description,
        quantity=item.quantity,
        location=item.location,
        status='available',
        brand=item.brand,
        created_by=current_user.id,
        team_id=current_user.team_id
    )
    
    # Copy categories
    for category in item.categories:
        new_item.categories.append(category)
    
    db.session.add(new_item)
    
    # Log action
    log = Log(
        user_id=current_user.id,
        item_id=new_item.id,
        action='created',
        details=f'Dupliziert von {item.item_uid}'
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Artikel {new_item.item_uid} wurde erstellt', 'success')
    return redirect(url_for('items.detail', id=new_item.id))

@items.route("/<int:id>/quick-edit")
@login_required
def quick_edit(id):
    """Show quick edit form for HTMX"""
    item = Item.query.get_or_404(id)
    
    # Check permissions
    if not current_user.is_admin() and item.team_id != current_user.team_id:
        abort(403)
    
    return render_template('items/partials/quick_edit.html', item=item)
# Füge diese Routes zu app/items/routes.py hinzu:

@items.route("/search")
@login_required
def search():
    """Search for items by UID - used by scanner"""
    item_uid = request.args.get('item_uid', '').strip()
    
    if not item_uid:
        return '<p class="text-muted">Bitte geben Sie eine Artikel-ID ein.</p>'
    
    # Suche nach exakter ID
    item = Item.query.filter_by(item_uid=item_uid).first()
    
    if item:
        # Prüfe Berechtigung
        if not current_user.is_admin() and item.team_id != current_user.team_id:
            return '<div class="alert alert-warning">Keine Berechtigung für diesen Artikel.</div>'
        
        # Return redirect für HTMX
        return f'''
        <div class="alert alert-success">
            <h5>Artikel gefunden!</h5>
            <p>{item.name} ({item.item_uid})</p>
            <a href="/items/{item.id}" class="btn btn-primary btn-sm">
                <i class="bi bi-eye"></i> Artikel anzeigen
            </a>
        </div>
        '''
    else:
        # Suche nach ähnlichen
        similar = Item.query.filter(
            Item.item_uid.like(f'%{item_uid}%')
        ).limit(5).all()
        
        if similar:
            html = '<div class="alert alert-info"><p>Artikel nicht gefunden. Meinten Sie:</p><ul>'
            for item in similar:
                if current_user.is_admin() or item.team_id == current_user.team_id:
                    html += f'<li><a href="/items/{item.id}">{item.item_uid} - {item.name}</a></li>'
            html += '</ul></div>'
            return html
        else:
            return '<div class="alert alert-danger">Artikel nicht gefunden.</div>'


@items.route("/recent-scans")
@login_required
def recent_scans():
    """Get recent item views for current user"""
    # Hole die letzten angesehenen Artikel
    recent_logs = Log.query.filter_by(
        user_id=current_user.id,
        action='view'
    ).order_by(Log.timestamp.desc()).limit(5).all()
    
    if not recent_logs:
        return '<p class="text-muted">Noch keine Scans vorhanden.</p>'
    
    html = '<div class="list-group">'
    for log in recent_logs:
        if log.item:  # Falls Item noch existiert
            html += f'''
            <a href="/items/{log.item.id}" class="list-group-item list-group-item-action">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>{log.item.item_uid}</strong> - {log.item.name}
                    </div>
                    <small class="text-muted">{log.timestamp.strftime('%H:%M')}</small>
                </div>
            </a>
            '''
    html += '</div>'
    
    return html
