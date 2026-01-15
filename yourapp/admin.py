from django.contrib import admin
from .models import Property, Booking, Profile

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_from', 'beds', 'baths', 'is_featured', 'show_on_homepage', 'homepage_order', 'created_at')
    list_filter = ('is_featured', 'show_on_homepage', 'beds', 'baths')
    search_fields = ('title', 'description', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('show_on_homepage', 'homepage_order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'image')
        }),
        ('Property Details', {
            'fields': ('price_from', 'beds', 'baths', 'capacity', 'parking', 'distance_to_stadium_mins')
        }),
        ('Search & SEO', {
            'fields': ('tags', 'keywords')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'show_on_homepage', 'homepage_order'),
            'description': 'Control where this property appears on the website. Set "Show on homepage" and adjust "Homepage order" to feature in the Top Properties section.'
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'guest_name', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status', 'check_in')
    search_fields = ('guest_name', 'guest_email', 'booking_reference')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'company_name', 'phone_number', 'booking_purpose')
    list_filter = ('account_type',)
    search_fields = ('user__username', 'user__email', 'company_name', 'phone_number')
    readonly_fields = ('user',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'booking_purpose')
        }),
        ('Account Type', {
            'fields': ('account_type',)
        }),
        ('Business Details', {
            'fields': ('company_name', 'company_address', 'job_title', 'company_vat', 'company_registration_number'),
            'classes': ('collapse',),
            'description': 'These fields are only relevant for business accounts.'
        }),
    )
