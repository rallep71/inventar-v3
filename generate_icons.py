#!/usr/bin/env python3
"""
Icon Generator für PWA
Erstellt alle benötigten Icon-Größen aus einem Source-Icon
"""
import os
from PIL import Image, ImageDraw

def create_app_icon(size, output_path):
    """Erstelle ein einfaches App-Icon mit Box-Symbol"""
    # Create image with white background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Blue background circle
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(13, 110, 253, 255))  # Bootstrap primary color
    
    # Draw box icon
    box_margin = size // 3
    box_size = size - (2 * box_margin)
    
    # Box body
    draw.rectangle([box_margin, box_margin + box_size//4, 
                   size-box_margin, size-box_margin], 
                   fill=(255, 255, 255, 255))
    
    # Box lid (trapezoid)
    lid_points = [
        (box_margin - box_size//8, box_margin + box_size//4),
        (size-box_margin + box_size//8, box_margin + box_size//4),
        (size-box_margin, box_margin),
        (box_margin, box_margin)
    ]
    draw.polygon(lid_points, fill=(255, 255, 255, 255))
    
    # Save
    img.save(output_path, 'PNG')
    print(f"Created: {output_path}")

def generate_all_icons():
    """Generate all required icon sizes"""
    # Icon sizes needed for PWA
    sizes = [16, 32, 72, 96, 128, 144, 192, 384, 512]
    
    # Create icons directory
    icon_dir = 'app/static/icons'
    os.makedirs(icon_dir, exist_ok=True)
    
    # Generate each size
    for size in sizes:
        output_path = os.path.join(icon_dir, f'icon-{size}x{size}.png')
        create_app_icon(size, output_path)
    
    # Create special icons
    create_app_icon(72, os.path.join(icon_dir, 'badge-72x72.png'))
    
    print("\n✅ Alle Icons wurden erfolgreich generiert!")
    print(f"📁 Icons gespeichert in: {icon_dir}")

if __name__ == '__main__':
    generate_all_icons()
