import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeletstays.settings')
django.setup()

from yourapp.models import Property

def populate():
    properties = [
        {
            'title': 'The Stadium View Apartment',
            'slug': 'stadium-view-apartment',
            'short_description': 'A stunning 2-bedroom apartment with panoramic views of Bramall Lane. Perfect for football fans, corporate visitors, and families looking for a comfortable base in Sheffield.',
            'description': 'A stunning 2-bedroom apartment with panoramic views of Bramall Lane. Perfect for football fans, corporate visitors, and families looking for a comfortable base in Sheffield. Full amenities included.',
            'image': 'properties/stadium-apt.jpg',
            'price_from': 85,
            'beds': 2,
            'baths': 1,
            'capacity': 4,
            'parking': True,
            'distance_to_stadium_mins': 5,
            'is_featured': True,
            'tags': 'view, stadium, luxury',
            'keywords': 'sheffield, football, apartment'
        },
        {
            'title': 'City Centre Studio',
            'slug': 'city-centre-studio',
            'short_description': 'Modern studio apartment in the heart of Sheffield. Ideal for solo travellers and contractors.',
            'description': 'Modern studio apartment in the heart of Sheffield. Ideal for solo travellers and contractors. Close to all transport links.',
            'image': 'properties/CityCentre-apt.jpg',
            'price_from': 55,
            'beds': 1,
            'baths': 1,
            'capacity': 2,
            'parking': False,
            'distance_to_stadium_mins': 15,
            'is_featured': False,
            'tags': 'city-centre, studio, modern',
            'keywords': 'sheffield, studio, cheap'
        },
        {
            'title': 'Hillsborough Family Home',
            'slug': 'hillsborough-family-home',
            'short_description': 'Spacious 3-bedroom house near Hillsborough Stadium. Great for families and groups.',
            'description': 'Spacious 3-bedroom house near Hillsborough Stadium. Great for families and groups. Large garden and parking.',
            'image': 'properties/hillsborough-apt.jpg',
            'price_from': 120,
            'beds': 3,
            'baths': 2,
            'capacity': 6,
            'parking': True,
            'distance_to_stadium_mins': 8,
            'is_featured': False,
            'tags': 'family, house, garden',
            'keywords': 'hillsborough, family, house'
        },
        {
            'title': 'Contractor\'s Retreat',
            'slug': 'contractors-retreat',
            'short_description': 'Purpose-built accommodation for contractors. Weekly and monthly rates available.',
            'description': 'Purpose-built accommodation for contractors. Weekly and monthly rates available. High speed wifi and workspace.',
            'image': 'properties/Retreat-apt.jpg',
            'price_from': 45,
            'beds': 1,
            'baths': 1,
            'capacity': 2,
            'parking': True,
            'distance_to_stadium_mins': 20,
            'is_featured': False,
            'tags': 'contractor, work, wifi',
            'keywords': 'contractor, cheap, long-term'
        },
    ]

    for prop_data in properties:
        Property.objects.get_or_create(slug=prop_data['slug'], defaults=prop_data)
        print(f"Created/Updated: {prop_data['title']}")

if __name__ == '__main__':
    populate()
