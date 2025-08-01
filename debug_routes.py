#!/usr/bin/env python3
"""
Debug script to show all registered routes
Run: python debug_routes.py
"""
from app import create_app

app = create_app()

print("🔍 Registrierte Routes:\n")
print(f"{'Route':<40} {'Methods':<20} {'Endpoint'}")
print("-" * 80)

with app.app_context():
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"{str(rule):<40} {methods:<20} {rule.endpoint}")

print("\n📦 Registrierte Blueprints:")
for name, blueprint in app.blueprints.items():
    print(f"  - {name}")
