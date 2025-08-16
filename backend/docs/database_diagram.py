#!/usr/bin/env python3
"""
Database ERD Diagram Generator for Streamlink Dashboard

This script generates an Entity Relationship Diagram (ERD) from SQLAlchemy models
and saves it as both PNG and SVG formats.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from typing import Dict, List, Tuple
import os

# Set up the plotting style
plt.style.use('default')
sns.set_palette("husl")

def create_erd_diagram():
    """Create ERD diagram for Streamlink Dashboard database"""
    
    # Define the entities and their attributes
    entities = {
        'users': {
            'position': (1, 4),
            'attributes': [
                'id (PK)',
                'username (UNIQUE)',
                'password_hash',
                'is_admin',
                'is_active',
                'created_at',
                'last_login',
                'updated_at'
            ],
            'color': '#FF6B6B'
        },
        'platform_configs': {
            'position': (3, 4),
            'attributes': [
                'id (PK)',
                'platform',
                'stream_url_pattern',
                'quality_options',
                'default_quality',
                'additional_settings (JSON)',
                'created_at',
                'updated_at'
            ],
            'color': '#4ECDC4'
        },
        'system_configs': {
            'position': (5, 4),
            'attributes': [
                'id (PK)',
                'config_key (UNIQUE)',
                'config_value',
                'description',
                'created_at',
                'updated_at'
            ],
            'color': '#45B7D1'
        },
        'recording_schedules': {
            'position': (2, 2),
            'attributes': [
                'id (PK)',
                'platform',
                'streamer_id',
                'streamer_name',
                'quality',
                'output_path',
                'custom_arguments',
                'enabled',
                'created_at',
                'updated_at'
            ],
            'color': '#96CEB4'
        },
        'recordings': {
            'position': (4, 2),
            'attributes': [
                'id (PK)',
                'schedule_id (FK)',
                'file_path',
                'file_name',
                'file_size',
                'start_time',
                'end_time',
                'duration',
                'platform',
                'streamer_id',
                'streamer_name',
                'quality',
                'status',
                'is_favorite',
                'created_at',
                'updated_at'
            ],
            'color': '#FFEAA7'
        },
        'recording_jobs': {
            'position': (6, 2),
            'attributes': [
                'id (PK)',
                'schedule_id (FK)',
                'status',
                'start_time',
                'end_time',
                'error_message',
                'created_at',
                'updated_at'
            ],
            'color': '#DDA0DD'
        }
    }
    
    # Define relationships
    relationships = [
        ('recording_schedules', 'recordings', '1:N', 'has many'),
        ('recording_schedules', 'recording_jobs', '1:N', 'has many'),
        ('users', 'recording_schedules', '1:N', 'manages'),  # Implied relationship
    ]
    
    # Create the figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Draw entities
    entity_boxes = {}
    for entity_name, entity_data in entities.items():
        x, y = entity_data['position']
        color = entity_data['color']
        attributes = entity_data['attributes']
        
        # Calculate box dimensions
        max_attr_length = max(len(attr) for attr in attributes)
        box_width = max(3.5, max_attr_length * 0.15)
        box_height = len(attributes) * 0.3 + 0.8
        
        # Create entity box
        box = FancyBboxPatch(
            (x - box_width/2, y - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor='black',
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(box)
        
        # Add entity title
        ax.text(x, y + box_height/2 - 0.1, entity_name.upper(),
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
        
        # Add attributes
        for i, attr in enumerate(attributes):
            attr_y = y + box_height/2 - 0.4 - i * 0.3
            ax.text(x, attr_y, attr, ha='center', va='center', fontsize=9)
        
        entity_boxes[entity_name] = (x, y, box_width, box_height)
    
    # Draw relationships
    for rel in relationships:
        entity1, entity2, cardinality, label = rel
        
        if entity1 in entity_boxes and entity2 in entity_boxes:
            x1, y1, w1, h1 = entity_boxes[entity1]
            x2, y2, w2, h2 = entity_boxes[entity2]
            
            # Calculate connection points
            if x1 < x2:  # entity1 is to the left
                start_x = x1 + w1/2
                end_x = x2 - w2/2
            else:  # entity1 is to the right
                start_x = x1 - w1/2
                end_x = x2 + w2/2
            
            start_y = y1
            end_y = y2
            
            # Draw connection line
            ax.plot([start_x, end_x], [start_y, end_y], 'k-', linewidth=2, alpha=0.7)
            
            # Add cardinality labels
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            
            # Cardinality at start
            ax.text(start_x + (end_x - start_x) * 0.2, start_y + (end_y - start_y) * 0.2,
                   cardinality.split(':')[0], ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
            
            # Cardinality at end
            ax.text(start_x + (end_x - start_x) * 0.8, start_y + (end_y - start_y) * 0.8,
                   cardinality.split(':')[1], ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
            
            # Relationship label
            ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    # Add title
    ax.text(4, 5.5, 'Streamlink Dashboard Database Schema', 
            ha='center', va='center', fontsize=20, fontweight='bold')
    
    # Add legend
    legend_elements = [
        patches.Patch(color='#FF6B6B', label='Authentication'),
        patches.Patch(color='#4ECDC4', label='Platform Configuration'),
        patches.Patch(color='#45B7D1', label='System Configuration'),
        patches.Patch(color='#96CEB4', label='Scheduling'),
        patches.Patch(color='#FFEAA7', label='Recordings'),
        patches.Patch(color='#DDA0DD', label='Job Management')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))
    
    # Add notes
    notes = [
        "• PK = Primary Key",
        "• FK = Foreign Key", 
        "• UNIQUE = Unique Constraint",
        "• JSON = JSON data type",
        "• All tables include created_at, updated_at timestamps"
    ]
    
    for i, note in enumerate(notes):
        ax.text(0.1, 0.5 - i * 0.08, note, ha='left', va='center', fontsize=10,
               transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.2", 
               facecolor='lightgray', alpha=0.5))
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Generate and save the ERD diagram"""
    print("🔄 Generating database ERD diagram...")
    
    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    
    # Generate the diagram
    fig = create_erd_diagram()
    
    # Save as PNG
    png_path = 'docs/database_erd.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ PNG diagram saved: {png_path}")
    
    # Save as SVG
    svg_path = 'docs/database_erd.svg'
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"✅ SVG diagram saved: {svg_path}")
    
    # Save as PDF
    pdf_path = 'docs/database_erd.pdf'
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', facecolor='white')
    print(f"✅ PDF diagram saved: {pdf_path}")
    
    plt.close(fig)
    
    print("\n📊 Database ERD diagram generated successfully!")
    print("📁 Files saved in the 'docs' directory:")
    print(f"   • {png_path} (High-resolution PNG)")
    print(f"   • {svg_path} (Scalable SVG)")
    print(f"   • {pdf_path} (Print-ready PDF)")

if __name__ == "__main__":
    save_diagram()
