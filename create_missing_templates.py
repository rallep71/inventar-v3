#!/usr/bin/env python3
"""Create missing template files"""
import os

templates = {
    'app/templates/errors/404_partial.html': '''<div class="alert alert-danger">
    <h4 class="alert-heading">404 - Nicht gefunden</h4>
    <p>Die angeforderte Seite konnte nicht gefunden werden.</p>
</div>''',

    'app/templates/errors/500_partial.html': '''<div class="alert alert-danger">
    <h4 class="alert-heading">500 - Serverfehler</h4>
    <p>Es ist ein interner Fehler aufgetreten.</p>
</div>''',

    'app/templates/items/detail.html': '''{% extends "layout/base.html" %}

{% block title %}{{ item.name }} - Details{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1>{{ item.name }}</h1>
        <p class="text-muted">{{ item.item_uid }}</p>
        
        <div class="card mb-4">
            <div class="card-body">
                <h5 class="card-title">Details</h5>
                <dl class="row">
                    <dt class="col-sm-3">Menge:</dt>
                    <dd class="col-sm-9">{{ item.quantity }}</dd>
                    
                    <dt class="col-sm-3">Marke:</dt>
                    <dd class="col-sm-9">{{ item.brand or '-' }}</dd>
                    
                    <dt class="col-sm-3">Standort:</dt>
                    <dd class="col-sm-9">{{ item.location or '-' }}</dd>
                    
                    <dt class="col-sm-3">Zustand:</dt>
                    <dd class="col-sm-9">{{ item.condition or 'Gut' }}</dd>
                    
                    {% if item.notes %}
                    <dt class="col-sm-3">Notizen:</dt>
                    <dd class="col-sm-9">{{ item.notes }}</dd>
                    {% endif %}
                </dl>
            </div>
        </div>
        
        <div class="btn-group">
            <a href="{{ url_for('items.edit', id=item.id) }}" class="btn btn-primary">
                <i class="bi bi-pencil"></i> Bearbeiten
            </a>
            <button type="button" class="btn btn-danger" onclick="deleteItem({{ item.id }})">
                <i class="bi bi-trash"></i> Löschen
            </button>
            <a href="{{ url_for('items.index') }}" class="btn btn-secondary">
                <i class="bi bi-arrow-left"></i> Zurück
            </a>
        </div>
    </div>
    
    <div class="col-md-4">
        {% if item.image_file %}
        <img src="{{ url_for('static', filename='uploads/' + item.image_file) }}" 
             class="img-fluid rounded" alt="{{ item.name }}">
        {% else %}
        <div class="bg-light p-5 text-center rounded">
            <i class="bi bi-image" style="font-size: 3rem;"></i>
            <p>Kein Bild vorhanden</p>
        </div>
        {% endif %}
    </div>
</div>

<script>
function deleteItem(id) {
    if (confirm('Wirklich löschen?')) {
        fetch(`/items/${id}/delete`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}'
            }
        }).then(response => {
            if (response.ok) {
                window.location.href = '/items/';
            }
        });
    }
}
</script>
{% endblock %}''',

    'app/templates/items/add.html': '''{% extends "layout/base.html" %}

{% block title %}Neuer Artikel{% endblock %}

{% block content %}
<h1>Neuer Artikel</h1>

<form method="POST" enctype="multipart/form-data">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    
    <div class="row">
        <div class="col-md-8">
            <div class="mb-3">
                <label for="name" class="form-label">Name *</label>
                <input type="text" class="form-control" id="name" name="name" required>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="quantity" class="form-label">Menge *</label>
                        <input type="number" class="form-control" id="quantity" name="quantity" value="1" min="0" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="category_ids" class="form-label">Kategorie *</label>
                        <select class="form-select" id="category_ids" name="category_ids" required>
                            <option value="">Wählen...</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}">{{ category.name }} ({{ category.prefix }})</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="brand" class="form-label">Marke</label>
                        <input type="text" class="form-control" id="brand" name="brand">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="location" class="form-label">Standort</label>
                        <input type="text" class="form-control" id="location" name="location">
                    </div>
                </div>
            </div>
            
            <div class="mb-3">
                <label for="notes" class="form-label">Notizen</label>
                <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
            </div>
            
            <div class="mb-3">
                <label for="image" class="form-label">Bild</label>
                <input type="file" class="form-control" id="image" name="image" accept="image/*">
            </div>
            
            <button type="submit" class="btn btn-primary">Speichern</button>
            <a href="{{ url_for('items.index') }}" class="btn btn-secondary">Abbrechen</a>
        </div>
    </div>
</form>
{% endblock %}''',

    'app/templates/items/edit.html': '''{% extends "layout/base.html" %}

{% block title %}{{ item.name }} bearbeiten{% endblock %}

{% block content %}
<h1>Artikel bearbeiten</h1>

<form method="POST" enctype="multipart/form-data">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    
    <div class="row">
        <div class="col-md-8">
            <div class="mb-3">
                <label class="form-label">Item ID</label>
                <input type="text" class="form-control" value="{{ item.item_uid }}" readonly>
            </div>
            
            <div class="mb-3">
                <label for="name" class="form-label">Name *</label>
                <input type="text" class="form-control" id="name" name="name" value="{{ item.name }}" required>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="quantity" class="form-label">Menge *</label>
                        <input type="number" class="form-control" id="quantity" name="quantity" 
                               value="{{ item.quantity }}" min="0" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="category_ids" class="form-label">Kategorie *</label>
                        <select class="form-select" id="category_ids" name="category_ids" required>
                            {% for category in categories %}
                            <option value="{{ category.id }}" 
                                {% if category in item.categories %}selected{% endif %}>
                                {{ category.name }} ({{ category.prefix }})
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="brand" class="form-label">Marke</label>
                        <input type="text" class="form-control" id="brand" name="brand" 
                               value="{{ item.brand or '' }}">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="location" class="form-label">Standort</label>
                        <input type="text" class="form-control" id="location" name="location" 
                               value="{{ item.location or '' }}">
                    </div>
                </div>
            </div>
            
            <div class="mb-3">
                <label for="notes" class="form-label">Notizen</label>
                <textarea class="form-control" id="notes" name="notes" rows="3">{{ item.notes or '' }}</textarea>
            </div>
            
            <div class="mb-3">
                <label for="image" class="form-label">Neues Bild</label>
                <input type="file" class="form-control" id="image" name="image" accept="image/*">
                {% if item.image_file %}
                <small class="text-muted">Aktuelles Bild: {{ item.image_file }}</small>
                {% endif %}
            </div>
            
            <button type="submit" class="btn btn-primary">Speichern</button>
            <a href="{{ url_for('items.detail', id=item.id) }}" class="btn btn-secondary">Abbrechen</a>
        </div>
        
        <div class="col-md-4">
            {% if item.image_file %}
            <img src="{{ url_for('static', filename='uploads/' + item.image_file) }}" 
                 class="img-fluid rounded" alt="{{ item.name }}">
            {% endif %}
        </div>
    </div>
</form>
{% endblock %}'''
}

# Create templates
for path, content in templates.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {path}")

print("\n✅ All templates created!")
