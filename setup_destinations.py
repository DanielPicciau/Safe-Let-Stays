#!/usr/bin/env python
"""Setup script to create destinations and update property areas."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeletstays.settings')
django.setup()

from yourapp.models import Property, Destination

# Update existing properties with proper areas
Property.objects.filter(title__icontains='Stadium').update(area='Hillsborough', city='Sheffield')
Property.objects.filter(title__icontains='City Centre').update(area='City Centre', city='Sheffield')
Property.objects.filter(title__icontains='Hillsborough').update(area='Hillsborough', city='Sheffield')
Property.objects.filter(title__icontains='Retreat').update(area='Nether Edge', city='Sheffield')

print("Updated property areas:")
for p in Property.objects.all():
    print(f"  - {p.title}: {p.area}, {p.city}")

# Create suggested destinations
destinations = [
    {
        'name': 'Sheffield', 
        'subtitle': 'All properties in Sheffield', 
        'icon_name': 'city', 
        'icon_color': '#3B82F6', 
        'order': 1, 
        'filter_area': ''
    },
    {
        'name': 'City Centre', 
        'subtitle': 'Walking distance to shops & nightlife', 
        'icon_name': 'city', 
        'icon_color': '#8B5CF6', 
        'order': 2, 
        'filter_area': 'City Centre'
    },
    {
        'name': 'Hillsborough', 
        'subtitle': 'Near the football stadium', 
        'icon_name': 'stadium', 
        'icon_color': '#2E7D32', 
        'order': 3, 
        'filter_area': 'Hillsborough'
    },
    {
        'name': 'Nether Edge', 
        'subtitle': 'Peaceful residential area', 
        'icon_name': 'home', 
        'icon_color': '#F59E0B', 
        'order': 4, 
        'filter_area': 'Nether Edge'
    },
]

print("\nCreating destinations...")
for d in destinations:
    obj, created = Destination.objects.get_or_create(name=d['name'], defaults=d)
    status = "Created" if created else "Already exists"
    print(f"  - {obj.name}: {status}")

print("\nSetup complete!")
