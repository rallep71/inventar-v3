# app/items/routes.py
"""Items routes with HTMX support"""
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc
from app.items import items
from app.models.item import Item
from app.models.category import Category
from app.models.log import Log
from app.extensions import db
from app.utils.decorators import team_required
from app.utils.toast import htmx_toast, toast_redirect, toast_response
import json


@items.route("/")
@login_required
def index():
    """Items list with search, sort and pagination"""
    # Get parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'created_desc')
    category_id = request.args.get('category', type=int)
    location = request.args.get('location', '').strip()
    status = request.args.get('status', 'all')
    
    # Base query - filter by user's team if not admin
    query = Item.query
    if not current_user.is_admin():
        # Show items from user's teams
        team_ids = [team.id for team in current_user.teams]
        query = query.filter(Item.team_id.in_(team_ids))
    
    # Search filter
    if search:
        search_filter = or_(
            Item.name.ilike(f'%{search}%'),
            Item.item_uid.ilike(f'%{search}%'),
            Item.description.ilike(f'%{search}%'),
            Item.brand.ilike(f'%{search}%'),
            Item.model.ilike(f'%{search}%'),
            Item.barcode == search,
            Item.serial_number == search
        )
        query = query.filter(search_filter)
    
    # Category filter
    if category_id:
        query = query.join(Item.categories).filter(Category.id == category_id)
    
    # Location filter
    if location:
        location_filter = or_(
            Item.location.ilike(f'%{location}%'),
            Item.room.ilike(f'%{location}%'),
            Item.shelf.ilike(f'%{location}%')
        )
        query = query.filter(location_filter)
    
    # Status filter
    if status == 'available':
        query = query.filter(Item.quantity > 0, Item.is_sold == False, Item.is_borrowed == False)
    elif status == 'low_stock':
        query = query.filter(Item.quantity <= 5, Item.quantity > 0)
    elif status == 'out_of_stock':
        query = query.filter(Item.quantity <= 0)
    elif status == 'sold':
        query = query.filter(Item.is_sold == True)
    elif status == 'borrowed':
        query = query.filter(Item.is_borrowed == True)
    
    # Sorting
    sort_options = {
        'name_asc': Item.name.asc(),
        'name_desc': Item.name.desc(),
        'created_asc': Item.created_at.asc(),
        'created_desc': Item.created_at.desc(),
        'updated': Item.updated_at.desc(),
        'quantity_asc': Item.quantity.asc(),
        'quantity_desc': Item.quantity.desc(),
        'price_asc': Item.price.asc(),
        'price_desc': Item.price.desc(),
    }
    query = query.order_by(sort_options.get(sort, Item.created_at.desc()))
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items_list = pagination.items
    
    # Get categories for filter
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    
    # Get unique locations for filter
    locations = db.session.query(Item.room).filter(
        Item.room.isnot(None)
    ).distinct().order_by(Item.room).all()
    locations = [loc[0] for loc in locations if loc[0]]
    
    # Check if HTMX request for partial update
    if request.headers.get('HX-Request'):
        # Return only the items grid
        return render_template('items/partials/items_grid.html',
                             items=items_list,
                             pagination=pagination,
                             search=search,
                             sort=sort,
                             category_id=category_id,
                             location=location,
                             status=status)
    
    return render_template('items/index.html',
                         items=items_list,
                         pagination=pagination,
                         categories=categories,
                         locations=locations,
                         search=search,
                         sort=sort,
                         category_id=category_id,
                         location=location,
                         status=status)


@items.route("/search")
@login_required
def search():
    """Live search endpoint for typeahead"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'results': []})
    
    # Search items
    items_query = Item.query.filter(
        or_(
            Item.name.ilike(f'%{query}%'),
            Item.item_uid.ilike(f'%{query}%'),
            Item.brand.ilike(f'%{query}%')
        )
    ).limit(10)
    
    # Filter by team if not admin
    if not current_user.is_admin():
        team_ids = [team.id for team in current_user.teams]
        items_query = items_query.filter(Item.team_id.in_(team_ids))
    
    results = []
    for item in items_query:
        results.append({
            'id': item.id,
            'uid': item.item_uid,
            'name': item.name,
            'brand': item.brand or '',
            'quantity': item.quantity,
            'image': item.thumbnail_file or item.image_file,
            'url': url_for('items.detail', id=item.id)
        })
    
    return jsonify({'results': results})


@items.route("/<int:id>")
@login_required
def detail(id):
    """Item detail view"""
    item = Item.query.get_or_404(id)
    
    # Check access rights
    if not current_user.is_admin():
        team_ids = [team.id for team in current_user.teams]
        if item.team_id not in team_ids:
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
    
    return render_template('items/detail.html', 
                         item=item,
                         recent_logs=recent_logs)


@items.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    """Add new item"""
    if request.method == 'GET':
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        return render_template('items/add.html', categories=categories)
    
    # Handle POST - item creation
    # TODO: Implement form handling
    pass


@items.route("/<int:id>/edit", methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit item"""
    item = Item.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_admin() and item.created_by != current_user.id:
        flash('Sie können nur Ihre eigenen Artikel bearbeiten.', 'error')
        return redirect(url_for('items.detail', id=id))
    
    if request.method == 'GET':
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        return render_template('items/edit.html', item=item, categories=categories)
    
    # Handle POST - item update
    # TODO: Implement form handling
    pass


@items.route("/<int:id>/quick-update", methods=['POST'])
@login_required
def quick_update(id):
    """Quick update for quantity via HTMX"""
    item = Item.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_admin():
        team_ids = [team.id for team in current_user.teams]
        if item.team_id not in team_ids:
            return make_response('Keine Berechtigung', 403)
    
    # Get action
    action = request.form.get('action')
    
    if action == 'increment':
        item.quantity += 1
        message = f'Bestand erhöht auf {item.quantity}'
    elif action == 'decrement' and item.quantity > 0:
        item.quantity -= 1
        message = f'Bestand reduziert auf {item.quantity}'
    else:
        return make_response('Ungültige Aktion', 400)
    
    # Log action
    log = Log(
        user_id=current_user.id,
        item_id=item.id,
        action='quantity_update',
        details=f'{action}: {message}'
    )
    db.session.add(log)
    db.session.commit()
    
    # Return updated quantity badge
    response = make_response(render_template('items/partials/quantity_badge.html', item=item))
    return htmx_toast(response, message, 'success')


@items.route("/<int:id>/delete", methods=['POST'])
@login_required
def delete(id):
    """Delete item"""
    item = Item.query.get_or_404(id)
    
    # Check permission
    if not current_user.is_admin() and item.created_by != current_user.id:
        return toast_response('Keine Berechtigung zum Löschen', 'error')
    
    # Log deletion
    log = Log(
        user_id=current_user.id,
        action='delete',
        details=f'Artikel {item.item_uid} ({item.name}) gelöscht'
    )
    db.session.add(log)
    
    # Delete item
    db.session.delete(item)
    db.session.commit()
    
    return toast_redirect(url_for('items.index'), 
                         f'Artikel {item.name} wurde gelöscht', 
                         'success')


@items.route("/scan")
@login_required
def scan():
    """QR code scanner page"""
    return render_template('items/scan.html')


@items.route("/scan/process", methods=['POST'])
@login_required
def process_scan():
    """Process scanned QR code"""
    data = request.get_json()
    code = data.get('code', '').strip()
    
    if not code:
        return jsonify({'error': 'Kein Code empfangen'}), 400
    
    # Try to find item by UID or barcode
    item = Item.query.filter(
        or_(Item.item_uid == code, Item.barcode == code)
    ).first()
    
    if item:
        # Check access
        if not current_user.is_admin():
            team_ids = [team.id for team in current_user.teams]
            if item.team_id not in team_ids:
                return jsonify({'error': 'Keine Berechtigung'}), 403
        
        return jsonify({
            'found': True,
            'url': url_for('items.detail', id=item.id),
            'item': {
                'id': item.id,
                'uid': item.item_uid,
                'name': item.name,
                'quantity': item.quantity
            }
        })
    
    return jsonify({
        'found': False,
        'message': 'Artikel nicht gefunden'
    })
