from django.core.management.base import BaseCommand
from yourapp.models import Booking
from yourapp.utils import send_receipt_email

class Command(BaseCommand):
    help = 'Manually send a receipt email for a specific booking.'

    def add_arguments(self, parser):
        parser.add_argument('booking_id', type=int, help='The ID of the booking')

    def handle(self, *args, **options):
        booking_id = options['booking_id']
        try:
            booking = Booking.objects.get(id=booking_id)
            self.stdout.write(f"Found booking #{booking.id} for {booking.guest_email}")
            
            # Force regeneration of receipt for testing purposes
            self.stdout.write("Clearing existing receipt to force regeneration with new logo...")
            booking.receipt_pdf = None
            booking.save()

            self.stdout.write("Attempting to send receipt email...")
            send_receipt_email(booking)
            self.stdout.write(self.style.SUCCESS("Process completed. Check console for MailerSend output."))
            
        except Booking.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Booking with ID {booking_id} does not exist."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
