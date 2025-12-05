from django.core.management.base import BaseCommand
from yourapp.models import Booking
from yourapp.utils import generate_receipt_pdf

class Command(BaseCommand):
    help = 'Generates PDF receipts for confirmed bookings that do not have one.'

    def handle(self, *args, **options):
        bookings = Booking.objects.filter(status='confirmed', receipt_pdf='')
        count = bookings.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No missing receipts found.'))
            return

        self.stdout.write(f'Found {count} confirmed bookings without receipts. Generating...')
        
        for booking in bookings:
            try:
                generate_receipt_pdf(booking)
                self.stdout.write(self.style.SUCCESS(f'Generated receipt for Booking #{booking.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to generate receipt for Booking #{booking.id}: {e}'))
                
        self.stdout.write(self.style.SUCCESS('Done.'))
