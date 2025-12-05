from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import builtins

class Property(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField(help_text="Displayed on cards")
    description = models.TextField(help_text="Full description for the property page")
    
    # Image handling
    image = models.ImageField(upload_to='properties/', blank=True, null=True)
    
    # Key details
    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    beds = models.IntegerField()
    baths = models.IntegerField()
    capacity = models.IntegerField(help_text="Maximum number of guests")
    parking = models.BooleanField(default=False)
    distance_to_stadium_mins = models.IntegerField(help_text="Minutes to stadium", default=0)
    
    # Search & SEO
    tags = models.CharField(max_length=500, blank=True, help_text="Comma separated tags")
    keywords = models.TextField(blank=True, help_text="Keywords for search optimization")
    
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # =========================================================================
    # GUESTY INTEGRATION FIELDS (Uncomment when ready to use)
    # =========================================================================
    # guesty_listing_id = models.CharField(
    #     max_length=100, 
    #     blank=True, 
    #     null=True,
    #     db_index=True,
    #     help_text="Guesty listing ID for API integration"
    # )
    # guesty_last_synced = models.DateTimeField(
    #     blank=True, 
    #     null=True,
    #     help_text="Last time property was synced with Guesty"
    # )
    # =========================================================================

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('property_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    class Meta:
        verbose_name_plural = "Properties"


# =============================================================================
# BOOKING MODEL
# =============================================================================
from django.conf import settings

class Booking(models.Model):
    """
    Local booking record that syncs with Guesty reservations.
    """
    STATUS_CHOICES = [
        ('inquiry', 'Inquiry'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    
    SOURCE_CHOICES = [
        ('direct', 'Direct Website'),
        ('guesty', 'Guesty'),
        ('airbnb', 'Airbnb'),
        ('booking', 'Booking.com'),
        ('vrbo', 'VRBO'),
        ('other', 'Other'),
    ]
    
    # Property reference
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )

    # User reference (optional, for logged in users)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    
    # Guesty sync
    guesty_reservation_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        db_index=True,
        help_text="Guesty reservation ID for sync"
    )

    # Stripe sync
    stripe_session_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_index=True
    )
    
    # Guest information
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=50, blank=True)
    
    # Booking dates
    check_in = models.DateField(db_index=True)
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    
    # Status and source
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='inquiry'
    )
    source = models.CharField(
        max_length=20, 
        choices=SOURCE_CHOICES, 
        default='direct'
    )
    
    # Pricing
    nightly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    cleaning_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        default=0
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Notes
    guest_notes = models.TextField(
        blank=True, 
        help_text="Notes from the guest"
    )
    internal_notes = models.TextField(
        blank=True, 
        help_text="Internal staff notes"
    )
    
    # Receipt
    receipt_pdf = models.FileField(upload_to='receipts/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-check_in']
        indexes = [
            models.Index(fields=['property', 'check_in']),
            models.Index(fields=['status', 'check_in']),
        ]
    
    def __str__(self):
        return f"{self.property.title} - {self.guest_name} ({self.check_in} to {self.check_out})"
    
    @builtins.property
    def nights(self):
        """Calculate number of nights."""
        return (self.check_out - self.check_in).days
    
    def calculate_total(self):
        """Calculate total price based on nightly rate and fees."""
        if self.nightly_rate:
            subtotal = self.nightly_rate * self.nights
            cleaning = self.cleaning_fee or 0
            return subtotal + cleaning
        return None
    
    def save(self, *args, **kwargs):
        # Auto-calculate total if not set
        if not self.total_price and self.nightly_rate:
            self.total_price = self.calculate_total()
        super().save(*args, **kwargs)


from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    booking_purpose = models.CharField(max_length=200, blank=True, help_text="What are you booking for?")

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
