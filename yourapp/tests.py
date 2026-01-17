"""
Safe Let Stays - Unit Tests
============================
Comprehensive test suite for the Safe Let Stays application.

Run tests with:
    python manage.py test yourapp.tests

Or with pytest:
    pytest
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

from .models import Property, Booking, Profile, Destination


class PropertyModelTest(TestCase):
    """Tests for the Property model."""

    def setUp(self):
        self.property = Property.objects.create(
            title='Test Sheffield Apartment',
            short_description='A lovely apartment in the city centre.',
            description='Full description of the lovely apartment.',
            price_from=Decimal('85.00'),
            beds=2,
            baths=1,
            capacity=4,
            parking=True,
            area='City Centre',
            city='Sheffield',
            distance_to_stadium_mins=10
        )

    def test_property_creation(self):
        """Test that a property is created correctly."""
        self.assertEqual(self.property.title, 'Test Sheffield Apartment')
        self.assertEqual(self.property.price_from, Decimal('85.00'))
        self.assertEqual(self.property.beds, 2)

    def test_property_slug_auto_generation(self):
        """Test that slug is auto-generated from title."""
        self.assertEqual(self.property.slug, 'test-sheffield-apartment')

    def test_property_str_method(self):
        """Test the string representation."""
        self.assertEqual(str(self.property), 'Test Sheffield Apartment')

    def test_property_get_absolute_url(self):
        """Test the get_absolute_url method."""
        url = self.property.get_absolute_url()
        self.assertEqual(url, '/property/test-sheffield-apartment/')

    def test_property_tags_list(self):
        """Test the get_tags_list method."""
        self.property.tags = 'wifi, city-centre, parking'
        self.property.save()
        tags = self.property.get_tags_list()
        self.assertEqual(tags, ['wifi', 'city-centre', 'parking'])


class BookingModelTest(TestCase):
    """Tests for the Booking model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.property = Property.objects.create(
            title='Test Property',
            short_description='Short description',
            description='Full description',
            price_from=Decimal('100.00'),
            beds=2,
            baths=1,
            capacity=4,
        )
        self.booking = Booking.objects.create(
            property=self.property,
            user=self.user,
            guest_name='John Doe',
            guest_email='john@example.com',
            check_in=date.today() + timedelta(days=7),
            check_out=date.today() + timedelta(days=10),
            guests=2,
            nightly_rate=Decimal('100.00'),
            status='confirmed'
        )

    def test_booking_creation(self):
        """Test that a booking is created correctly."""
        self.assertEqual(self.booking.guest_name, 'John Doe')
        self.assertEqual(self.booking.status, 'confirmed')

    def test_booking_nights_calculation(self):
        """Test the nights property calculation."""
        self.assertEqual(self.booking.nights, 3)

    def test_booking_total_calculation(self):
        """Test the calculate_total method."""
        total = self.booking.calculate_total()
        self.assertEqual(total, Decimal('300.00'))

    def test_booking_str_method(self):
        """Test the string representation."""
        expected = f"Test Property - John Doe ({self.booking.check_in} to {self.booking.check_out})"
        self.assertEqual(str(self.booking), expected)


class ProfileModelTest(TestCase):
    """Tests for the Profile model."""

    def test_profile_auto_creation(self):
        """Test that profile is automatically created for new users."""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)

    def test_business_account(self):
        """Test business account functionality."""
        user = User.objects.create_user(
            username='businessuser',
            email='business@example.com',
            password='businesspass123'
        )
        user.profile.account_type = 'business'
        user.profile.company_name = 'Test Company Ltd'
        user.profile.save()
        
        self.assertTrue(user.profile.is_business_account)
        self.assertEqual(user.profile.company_name, 'Test Company Ltd')


class HomepageViewTest(TestCase):
    """Tests for homepage view."""

    def setUp(self):
        self.client = Client()

    def test_homepage_returns_200(self):
        """Test homepage returns 200 status."""
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        """Test homepage uses the correct template."""
        response = self.client.get(reverse('homepage'))
        self.assertTemplateUsed(response, 'homepage.html')


class PropertiesViewTest(TestCase):
    """Tests for properties view."""

    def setUp(self):
        self.client = Client()
        self.property = Property.objects.create(
            title='Test Property',
            short_description='Short description',
            description='Full description',
            price_from=Decimal('100.00'),
            beds=3,
            baths=2,
            capacity=6,
        )

    def test_properties_view_returns_200(self):
        """Test properties view returns 200 status."""
        response = self.client.get(reverse('properties'))
        self.assertEqual(response.status_code, 200)

    def test_properties_view_contains_property(self):
        """Test that properties are in context."""
        response = self.client.get(reverse('properties'))
        self.assertIn(self.property, response.context['properties'])

    def test_properties_filter_by_capacity(self):
        """Test filtering by guest capacity."""
        response = self.client.get(reverse('properties'), {'guests': '4'})
        self.assertIn(self.property, response.context['properties'])
        
        response = self.client.get(reverse('properties'), {'guests': '10'})
        self.assertNotIn(self.property, list(response.context['properties']))


class PropertyDetailViewTest(TestCase):
    """Tests for property detail view."""

    def setUp(self):
        self.client = Client()
        self.property = Property.objects.create(
            title='Detailed Test Property',
            short_description='Short description',
            description='Full description',
            price_from=Decimal('100.00'),
            beds=2,
            baths=1,
            capacity=4,
        )

    def test_property_detail_returns_200(self):
        """Test property detail returns 200 for valid slug."""
        response = self.client.get(
            reverse('property_detail', kwargs={'slug': self.property.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_property_detail_returns_404_for_invalid_slug(self):
        """Test property detail returns 404 for invalid slug."""
        response = self.client.get(
            reverse('property_detail', kwargs={'slug': 'non-existent-property'})
        )
        self.assertEqual(response.status_code, 404)


class AuthenticationTest(TestCase):
    """Tests for authentication views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_page_returns_200(self):
        """Test login page returns 200."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        """Test login with valid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page


class StaffPanelAccessTest(TestCase):
    """Tests for staff panel access control."""

    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staffpass123',
            is_staff=True
        )

    def test_staff_panel_requires_authentication(self):
        """Test that staff panel redirects unauthenticated users."""
        response = self.client.get(reverse('staff_panel'))
        self.assertEqual(response.status_code, 302)

    def test_regular_user_cannot_access_staff_panel(self):
        """Test that regular users are redirected from staff panel."""
        self.client.login(username='regular', password='regularpass123')
        response = self.client.get(reverse('staff_panel'))
        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_access_staff_panel(self):
        """Test that staff users can access staff panel."""
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get(reverse('staff_panel'))
        self.assertEqual(response.status_code, 200)


class MyBookingsViewTest(TestCase):
    """Tests for my bookings view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_my_bookings_requires_login(self):
        """Test that my bookings redirects unauthenticated users."""
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 302)

    def test_my_bookings_returns_200_for_authenticated_user(self):
        """Test my bookings returns 200 for logged in users."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
