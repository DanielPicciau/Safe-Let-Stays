from django.contrib import admin
from .models import Property, Booking

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_from', 'beds', 'baths', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'beds', 'baths')
    search_fields = ('title', 'description', 'short_description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'guest_name', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status', 'check_in')
    search_fields = ('guest_name', 'guest_email', 'booking_reference')
