# =============================================================================
# Safe Let Stays - Pytest Configuration
# =============================================================================
# This file provides fixtures and configuration for pytest-django tests.
# =============================================================================

import pytest
from django.contrib.auth.models import User


@pytest.fixture
def user(db):
    """Create a regular user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def staff_user(db):
    """Create a staff user for testing admin views."""
    return User.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password='staffpassword123',
        is_staff=True,
        first_name='Staff',
        last_name='User'
    )


@pytest.fixture
def superuser(db):
    """Create a superuser for testing."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def sample_property(db):
    """Create a sample property for testing."""
    from yourapp.models import Property
    return Property.objects.create(
        title='Test Property',
        slug='test-property',
        short_description='A test property for unit tests.',
        description='This is a detailed description of the test property.',
        price_from=100.00,
        beds=2,
        baths=1,
        capacity=4,
        parking=True,
        area='City Centre',
        city='Sheffield',
        postcode='S1 1AA',
        distance_to_stadium_mins=5
    )


@pytest.fixture
def sample_booking(db, sample_property, user):
    """Create a sample booking for testing."""
    from yourapp.models import Booking
    from datetime import date, timedelta
    
    return Booking.objects.create(
        booked_property=sample_property,
        user=user,
        guest_name='Test Guest',
        guest_email='guest@example.com',
        guest_phone='+44 123 456 7890',
        check_in=date.today() + timedelta(days=7),
        check_out=date.today() + timedelta(days=10),
        guests=2,
        total_price=300.00,
        status='confirmed'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return a client logged in as a regular user."""
    client.login(username='testuser', password='testpassword123')
    return client


@pytest.fixture
def staff_client(client, staff_user):
    """Return a client logged in as a staff member."""
    client.login(username='staffuser', password='staffpassword123')
    return client
