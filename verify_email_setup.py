import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeletstays.settings_production')
django.setup()

from yourapp.models import Property, Booking
from yourapp.utils import send_receipt_email

def create_and_test():
    print("🚀 Starting Email Verification Test...")
    
    # 1. Get or Create a Property
    property_obj = Property.objects.first()
    if not property_obj:
        print("   No properties found. Creating a test property...")
        property_obj = Property.objects.create(
            title="Test Property",
            description="A test property for email verification",
            short_description="A short description for the test property",
            price_from=100,
            capacity=2,
            beds=1,
            baths=1
        )
    
    print(f"   Using Property: {property_obj.title}")

    # 2. Create a Test Booking
    print("   Creating a test booking...")
    booking = Booking.objects.create(
        property=property_obj,
        guest_name="Test User",
        guest_email="danieljunior.business@gmail.com", 
        check_in=timezone.now().date(),
        check_out=timezone.now().date() + timedelta(days=2),
        guests=1,
        status='confirmed',
        nightly_rate=100,
        total_price=200
    )
    
    print(f"   Created Booking #{booking.id} for {booking.guest_email}")

    # 3. Send Receipt
    print("   Attempting to send receipt...")
    try:
        send_receipt_email(booking)
        print("✅ Email sending function completed successfully.")
        print(f"   Please check the inbox for: {booking.guest_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    create_and_test()
