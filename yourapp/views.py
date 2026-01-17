from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.exceptions import PermissionDenied
from django.core.signing import Signer, BadSignature
from django.utils.html import escape
from django.utils import timezone
import stripe
import logging
import json
from datetime import datetime
from .models import Property, Booking, Destination, RecentSearch
from .forms import PropertyForm, CheckoutForm, BookingSearchForm
from .utils import generate_receipt_pdf, send_receipt_email
from .security import rate_limit, get_client_ip, InputValidator, SecurityLogger

logger = logging.getLogger(__name__)

# Constants
HOMEPAGE_TOP_PROPERTIES_COUNT = 3
SIMILAR_PROPERTIES_COUNT = 3
RECENT_SEARCHES_COUNT = 3

# Signer for secure URL tokens
booking_signer = Signer(salt='booking-payment')


def csrf_failure(request, reason=""):
    """Custom CSRF failure view."""
    logger.warning(f"CSRF failure: {reason} from IP: {get_client_ip(request)}")
    return HttpResponseForbidden(
        "Security validation failed. Please refresh the page and try again."
    )

def get_common_context():
    """Get common context variables from settings."""
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'Safe Let Stays'),
        'brand_color': getattr(settings, 'BRAND_COLOR', '#2E7D32'),
        'contact_phone': getattr(settings, 'CONTACT_PHONE', '+44 114 123 4567'),
        'contact_email': getattr(settings, 'CONTACT_EMAIL', 'hello@safeletstays.co.uk'),
        'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Sheffield Street, Sheffield, S1 1AA'),
    }

def homepage(request):
    """Render the homepage with database context data."""
    context = get_common_context()
    
    # Optimized query: Get all needed properties in fewer queries
    all_properties = list(Property.objects.all()[:HOMEPAGE_TOP_PROPERTIES_COUNT + 1])
        
    # Featured Property - try to find featured, fallback to first
    featured = None
    for prop in all_properties:
        if prop.is_featured:
            featured = prop
            break
    if not featured and all_properties:
        featured = all_properties[0]
        
    context['featured_property'] = featured
    
    # Top Properties for homepage section (selected by staff)
    top_properties = list(Property.objects.filter(show_on_homepage=True).order_by('homepage_order')[:HOMEPAGE_TOP_PROPERTIES_COUNT])
    if len(top_properties) < HOMEPAGE_TOP_PROPERTIES_COUNT:
        # Fallback to first properties if not enough are selected
        top_properties = all_properties[:HOMEPAGE_TOP_PROPERTIES_COUNT]
    context['top_properties'] = top_properties
    
    # Destinations for search dropdown - will use json_script in template
    destinations = Destination.objects.filter(is_active=True).order_by('order')
    destinations_list = list(destinations.values('name', 'subtitle', 'icon_name', 'icon_color', 'filter_area'))
    context['destinations_json'] = json.dumps(destinations_list)
    
    # Recent searches (for logged in users or session)
    recent_searches = []
    if request.user.is_authenticated:
        recent_searches = RecentSearch.objects.filter(user=request.user)[:RECENT_SEARCHES_COUNT]
    elif request.session.session_key:
        recent_searches = RecentSearch.objects.filter(session_key=request.session.session_key)[:RECENT_SEARCHES_COUNT]
    
    # Convert dates to strings for JSON
    recent_list = []
    for search in recent_searches:
        recent_list.append({
            'location': search.location,
            'check_in': search.check_in.isoformat() if search.check_in else None,
            'check_out': search.check_out.isoformat() if search.check_out else None,
            'guests': search.guests
        })
    context['recent_searches_json'] = json.dumps(recent_list)
    
    return render(request, 'homepage.html', context)

def properties_view(request):
    context = get_common_context()
    properties = Property.objects.all()
    
    # Use form for validation (MED-04)
    form = BookingSearchForm(request.GET)
    
    # Get raw values for backward compatibility
    guests = request.GET.get('guests')
    beds = request.GET.get('beds')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    location = request.GET.get('location', '').strip()
    
    # Filter by location/area
    if location:
        properties = properties.filter(
            Q(area__icontains=location) | 
            Q(city__icontains=location) |
            Q(title__icontains=location)
        )
        
        # Save recent search with proper date parsing
        try:
            check_in_date = None
            check_out_date = None
            if check_in:
                check_in_date = timezone.datetime.strptime(check_in, settings.DATE_FORMAT_ISO).date()
            if check_out:
                check_out_date = timezone.datetime.strptime(check_out, settings.DATE_FORMAT_ISO).date()
            guests_int = int(guests) if guests and guests.isdigit() else 2
            
            # Create or update recent search
            if request.user.is_authenticated:
                RecentSearch.objects.update_or_create(
                    user=request.user,
                    location=location,
                    defaults={
                        'check_in': check_in_date,
                        'check_out': check_out_date,
                        'guests': guests_int,
                    }
                )
            else:
                # Ensure session exists
                if not request.session.session_key:
                    request.session.create()
                RecentSearch.objects.update_or_create(
                    session_key=request.session.session_key,
                    location=location,
                    defaults={
                        'check_in': check_in_date,
                        'check_out': check_out_date,
                        'guests': guests_int,
                    }
                )
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to save recent search: {e}")
    
    if guests:
        try:
            guests_val = int(guests)
            if 1 <= guests_val <= 100:  # Reasonable bounds
                properties = properties.filter(capacity__gte=guests_val)
        except ValueError:
            logger.debug(f"Invalid guests value: {guests}")
            
    if beds:
        try:
            beds_val = int(beds)
            if beds_val >= 4:
                properties = properties.filter(beds__gte=4)
            elif 1 <= beds_val <= 20:  # Reasonable bounds
                properties = properties.filter(beds=beds_val)
        except ValueError:
            logger.debug(f"Invalid beds value: {beds}")
            
    context['properties'] = properties
    context['search_params'] = {
        'guests': guests,
        'beds': beds,
        'check_in': check_in,
        'check_out': check_out,
        'location': location,
    }
    return render(request, 'properties.html', context)

def hosts_view(request):
    context = get_common_context()
    return render(request, 'hosts.html', context)

def reviews_view(request):
    context = get_common_context()
    return render(request, 'reviews.html', context)

def about_view(request):
    context = get_common_context()
    return render(request, 'about.html', context)

def property_detail_view(request, slug):
    """Display a single property with all its details."""
    context = get_common_context()
    property_obj = get_object_or_404(Property, slug=slug)
    
    # Get similar properties (same number of beds, excluding current)
    # Convert to list once to avoid multiple queries (CORR-02)
    similar_properties = list(
        Property.objects.filter(beds=property_obj.beds)
        .exclude(pk=property_obj.pk)[:SIMILAR_PROPERTIES_COUNT]
    )
    
    if len(similar_properties) < SIMILAR_PROPERTIES_COUNT:
        # Fill with other properties if not enough similar ones
        existing_pks = [p.pk for p in similar_properties] + [property_obj.pk]
        additional = list(
            Property.objects.exclude(pk__in=existing_pks)[:SIMILAR_PROPERTIES_COUNT - len(similar_properties)]
        )
        similar_properties = similar_properties + additional
    
    context['property'] = property_obj
    context['similar_properties'] = similar_properties
    return render(request, 'property_detail.html', context)

# Staff Panel Views
@staff_member_required
def staff_panel_view(request):
    from django.db.models import Avg, Sum
    properties = Property.objects.all().order_by('-created_at')
    
    # Calculate stats for the dashboard
    featured_count = properties.filter(is_featured=True).count()
    total_capacity = properties.aggregate(total=Sum('capacity'))['total'] or 0
    avg_price = properties.aggregate(avg=Avg('price_from'))['avg']
    avg_price = round(avg_price) if avg_price else 0
    
    context = {
        'properties': properties,
        'featured_count': featured_count,
        'total_capacity': total_capacity,
        'avg_price': avg_price,
    }
    return render(request, 'staff/panel.html', context)

@staff_member_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save()
            logger.info(f"Property created: {property_obj.title} by user: {request.user.username}")
            return redirect('staff_panel')
        else:
            # Log form errors at debug level to avoid leaking user data (MED-01)
            logger.debug(f"Property form validation failed for user: {request.user.username}")
    else:
        form = PropertyForm()
    
    return render(request, 'staff/property_form.html', {
        'form': form,
        'title': 'Add New Property'
    })

@staff_member_required
def edit_property_view(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            logger.info(f"Property updated: {property_obj.title} by user: {request.user.username}")
            return redirect('staff_panel')
        else:
            # Log form errors at debug level to avoid leaking user data (MED-01)
            logger.debug(f"Property edit form validation failed for user: {request.user.username}")
    else:
        form = PropertyForm(instance=property_obj)
    return render(request, 'staff/property_form.html', {'form': form, 'title': 'Edit Property'})

@staff_member_required
@require_POST
def delete_property_view(request, pk):
    from django.contrib import messages
    property_obj = get_object_or_404(Property, pk=pk)
    property_title = escape(property_obj.title)
    
    # Log the deletion
    logger.info(f"Property deleted: {property_title} by user: {request.user.username}")
    
    property_obj.delete()
    messages.success(request, f'Property "{property_title}" has been deleted.')
    return redirect('staff_panel')


# =============================================================================
# GUESTY API VIEWS (Uncomment when ready to use)
# =============================================================================
# 
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# import json
# 
# # Import Guesty integration (uncomment in guesty_integration.py first)
# # from .guesty_integration import (
# #     get_guesty_client, 
# #     get_property_blocked_dates,
# #     GuestyWebhookHandler,
# #     GUESTY_WEBHOOK_SECRET
# # )
# 
# 
# @require_http_methods(["GET"])
# def api_property_availability(request, property_id):
#     """
#     API endpoint to get property availability from Guesty.
#     
#     GET /api/properties/<id>/availability/?start=YYYY-MM-DD&end=YYYY-MM-DD
#     
#     Returns:
#         {
#             "property_id": 1,
#             "start_date": "2025-01-01",
#             "end_date": "2025-01-31",
#             "blocked_dates": ["2025-01-05", "2025-01-06", ...]
#         }
#     """
#     try:
#         property_obj = Property.objects.get(pk=property_id)
#     except Property.DoesNotExist:
#         return JsonResponse({'error': 'Property not found'}, status=404)
#     
#     start_date = request.GET.get('start')
#     end_date = request.GET.get('end')
#     
#     if not start_date or not end_date:
#         return JsonResponse({
#             'error': 'start and end date parameters required (YYYY-MM-DD format)'
#         }, status=400)
#     
#     # Check if property has Guesty listing ID
#     guesty_listing_id = getattr(property_obj, 'guesty_listing_id', None)
#     
#     if not guesty_listing_id:
#         # No Guesty integration - return empty blocked dates
#         return JsonResponse({
#             'property_id': property_id,
#             'start_date': start_date,
#             'end_date': end_date,
#             'blocked_dates': [],
#             'message': 'Property not linked to Guesty'
#         })
#     
#     try:
#         client = get_guesty_client()
#         blocked_dates = client.get_blocked_dates(
#             guesty_listing_id,
#             start_date,
#             end_date
#         )
#         
#         return JsonResponse({
#             'property_id': property_id,
#             'start_date': start_date,
#             'end_date': end_date,
#             'blocked_dates': blocked_dates,
#         })
#         
#     except ValueError as e:
#         # API key not configured
#         return JsonResponse({
#             'error': str(e)
#         }, status=503)
#     except Exception as e:
#         return JsonResponse({
#             'error': f'Failed to fetch availability: {str(e)}'
#         }, status=500)
# 
# 
# @require_http_methods(["POST"])
# def api_check_availability(request, property_id):
#     """
#     API endpoint to check if specific dates are available for booking.
#     
#     POST /api/properties/<id>/check-availability/
#     Body: {"check_in": "YYYY-MM-DD", "check_out": "YYYY-MM-DD", "guests": 2}
#     
#     Returns:
#         {
#             "available": true/false,
#             "unavailable_nights": [],
#             "pricing": {...},
#             "check_in": "2025-01-01",
#             "check_out": "2025-01-07",
#             "guests": 2
#         }
#     """
#     try:
#         property_obj = Property.objects.get(pk=property_id)
#     except Property.DoesNotExist:
#         return JsonResponse({'error': 'Property not found'}, status=404)
#     
#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON body'}, status=400)
#     
#     check_in = data.get('check_in')
#     check_out = data.get('check_out')
#     guests = data.get('guests', 1)
#     
#     if not check_in or not check_out:
#         return JsonResponse({
#             'error': 'check_in and check_out fields required (YYYY-MM-DD format)'
#         }, status=400)
#     
#     # Validate guest count against property capacity
#     if guests > property_obj.capacity:
#         return JsonResponse({
#             'available': False,
#             'error': f'Property maximum capacity is {property_obj.capacity} guests'
#         })
#     
#     # Check if property has Guesty listing ID
#     guesty_listing_id = getattr(property_obj, 'guesty_listing_id', None)
#     
#     if not guesty_listing_id:
#         # No Guesty integration - assume available
#         return JsonResponse({
#             'available': True,
#             'message': 'Property not managed by Guesty - please contact us to confirm availability',
#             'check_in': check_in,
#             'check_out': check_out,
#             'guests': guests
#         })
#     
#     try:
#         client = get_guesty_client()
#         result = client.check_availability(
#             guesty_listing_id,
#             check_in,
#             check_out,
#             guests
#         )
#         return JsonResponse(result)
#         
#     except ValueError as e:
#         return JsonResponse({
#             'error': str(e)
#         }, status=503)
#     except Exception as e:
#         return JsonResponse({
#             'error': f'Failed to check availability: {str(e)}'
#         }, status=500)
# 
# 
# @csrf_exempt
# @require_http_methods(["POST"])
# def guesty_webhook(request):
#     """
#     Webhook endpoint for Guesty events.
#     
#     POST /api/webhooks/guesty/
#     
#     Configure this URL in Guesty dashboard:
#     1. Go to Integrations > Webhooks
#     2. Add webhook URL: https://yourdomain.com/api/webhooks/guesty/
#     3. Select events: reservation.created, reservation.updated, 
#        reservation.canceled, calendar.updated
#     """
#     from django.conf import settings
#     
#     # Verify webhook signature if secret is configured
#     webhook_secret = getattr(settings, 'GUESTY_WEBHOOK_SECRET', '')
#     
#     if webhook_secret:
#         signature = request.headers.get('X-Guesty-Signature', '')
#         
#         if not GuestyWebhookHandler.verify_signature(
#             request.body, 
#             signature, 
#             webhook_secret
#         ):
#             return JsonResponse({
#                 'error': 'Invalid webhook signature'
#             }, status=401)
#     
#     try:
#         payload = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
#     
#     event_type = payload.get('event')
#     event_data = payload.get('data', {})
#     
#     if not event_type:
#         return JsonResponse({'error': 'Missing event type'}, status=400)
#     
#     # Process the webhook
#     try:
#         GuestyWebhookHandler.process_webhook(event_type, event_data)
#         return JsonResponse({
#             'status': 'received',
#             'event': event_type
#         })
#     except Exception as e:
#         # Log error but still return success to prevent retries
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.error(f"Error processing Guesty webhook: {str(e)}")
#         
#         return JsonResponse({
#             'status': 'received',
#             'warning': 'Event received but processing encountered an error'
#         })
# 
# =============================================================================

# =============================================================================
# STRIPE PAYMENT VIEWS
# =============================================================================

@require_POST
@rate_limit(key='checkout', max_requests=10, window=60)
def create_checkout_session(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Validate input using form
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        logger.warning(f"Invalid checkout form data from IP: {get_client_ip(request)}")
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    # Get validated data
    checkin = form.cleaned_data['checkin']
    checkout = form.cleaned_data['checkout']
    guests = form.cleaned_data['guests']
    
    # Validate dates
    if checkin >= checkout:
        return JsonResponse({'error': 'Check-out must be after check-in'}, status=400)
    
    nights = (checkout - checkin).days
    if nights < 1:
        nights = 1
    
    # Validate guest capacity
    if guests > property_obj.capacity:
        return JsonResponse({'error': f'Maximum capacity is {property_obj.capacity} guests'}, status=400)
    
    # Format dates for description using settings constants
    date_format = getattr(settings, 'DATE_FORMAT_DISPLAY', '%d %b %Y')
    date_range = f"{checkin.strftime(date_format)} - {checkout.strftime(date_format)}"
    description_parts = [date_range]
    description_parts.append(f"{nights} Night{'s' if nights > 1 else ''}")
    description_parts.append(f"{guests} Guest{'s' if guests != 1 else ''}")
    
    full_description = " • ".join(description_parts)
    
    # Get guest details (sanitized)
    if request.user.is_authenticated:
        guest_name = escape(request.user.get_full_name() or request.user.username)
        guest_email = request.user.email
        guest_phone = getattr(request.user.profile, 'phone_number', '') if hasattr(request.user, 'profile') else ''
    else:
        guest_name = escape(form.cleaned_data.get('guest_name') or 'Guest')
        guest_email = form.cleaned_data.get('guest_email') or ''
        guest_phone = form.cleaned_data.get('guest_phone') or ''
    
    # Get company details (for guest bookings)
    is_company_booking = form.cleaned_data.get('is_company_booking', False)
    company_name = escape(form.cleaned_data.get('company_name') or '')
    company_address = escape(form.cleaned_data.get('company_address') or '')
    company_vat = escape(form.cleaned_data.get('company_vat') or '')

    try:
        # Use atomic transaction to prevent race conditions (HIGH-04)
        with transaction.atomic():
            # Create pending booking (using booked_property to avoid shadowing builtin)
            booking = Booking.objects.create(
                booked_property=property_obj,
                user=request.user if request.user.is_authenticated else None,
                guest_name=guest_name,
                guest_email=guest_email,
                guest_phone=guest_phone,
                is_company_booking=is_company_booking,
                company_name=company_name,
                company_address=company_address,
                company_vat=company_vat,
                check_in=checkin,
                check_out=checkout,
                guests=guests,
                nightly_rate=property_obj.price_from,
                total_price=property_obj.price_from * nights,
                status='awaiting_payment'
            )

            # Create signed token for secure callback URLs (CRIT-04)
            signed_booking_id = booking_signer.sign(str(booking.id))

            # Construct image URL if available
            images = []
            if property_obj.image:
                image_url = request.build_absolute_uri(property_obj.image.url)
                # Only add image if it's likely accessible (not localhost)
                if 'localhost' not in image_url and '127.0.0.1' not in image_url:
                    images = [image_url]

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'gbp',
                            'unit_amount': int(property_obj.price_from * nights * 100),
                            'product_data': {
                                'name': f"Stay at {property_obj.title}",
                                'description': full_description,
                                'images': images,
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                customer_email=guest_email if guest_email else None,
                success_url=request.build_absolute_uri('/payment-success/') + f"?token={signed_booking_id}",
                cancel_url=request.build_absolute_uri('/payment-cancel/') + f"?token={signed_booking_id}",
                client_reference_id=str(booking.id),
                metadata={
                    'booking_id': booking.id,
                    'property_id': property_id,
                    'checkin': str(checkin),
                    'checkout': str(checkout),
                    'guests': guests,
                    'nights': nights
                }
            )
            
            # Update booking with session ID
            booking.stripe_session_id = checkout_session.id
            booking.save()
        
        logger.info(f"Checkout session created for booking {booking.id}")
        return redirect(checkout_session.url, code=303)
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during checkout: {str(e)}")
        return JsonResponse({'error': 'Payment processing error. Please try again.'}, status=500)
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)

def payment_success(request):
    """Handle payment success callback with signed token verification."""
    signed_token = request.GET.get('token')
    error_message = None
    success_message = None
    booking = None
    
    if not signed_token:
        logger.warning(f"Payment success attempt without token from IP: {get_client_ip(request)}")
        error_message = "Invalid payment link."
    else:
        try:
            # Verify the signed token (CRIT-04)
            booking_id = booking_signer.unsign(signed_token)
            logger.debug(f"payment_success view reached. Verified Booking ID: {booking_id}")
            
            booking = Booking.objects.get(id=int(booking_id))
            
            # Verify this is a legitimate payment completion
            # The booking should have a stripe_session_id and be awaiting payment
            if not booking.stripe_session_id:
                logger.warning(f"Payment success attempt without stripe session: {booking_id}")
                error_message = "Invalid payment session."
            else:
                should_send_email = False
                
                # Only confirm if it was awaiting payment
                if booking.status == 'awaiting_payment':
                    booking.status = 'confirmed'
                    booking.save()
                    should_send_email = True
                    logger.info(f"Booking {booking_id} confirmed via payment success view.")
                elif booking.status == 'confirmed':
                    # If confirmed but no receipt PDF, try sending again
                    if not booking.receipt_pdf:
                        should_send_email = True
                        logger.debug(f"Booking {booking_id} already confirmed but PDF missing. Retrying email.")
                    else:
                        success_message = "Booking confirmed. Receipt already sent."

                if should_send_email:
                    logger.debug(f"Sending receipt email for booking {booking_id}...")
                    try:
                        send_receipt_email(booking)
                        success_message = "Receipt sent successfully!"
                    except Exception as e:
                        logger.error(f"Error sending receipt email for booking {booking_id}: {e}")
                        error_message = "Booking confirmed, but failed to send email. Please contact support."
                     
        except BadSignature:
            logger.warning(f"Invalid signed token in payment_success from IP: {get_client_ip(request)}")
            error_message = "Invalid or expired payment link."
        except Booking.DoesNotExist:
            logger.warning(f"Payment success with non-existent booking from token")
            # Don't reveal if booking exists or not
            error_message = "Unable to process request. Please contact support."
        except Exception as e:
            logger.error(f"Error in payment_success view: {e}")
            error_message = "An error occurred. Please contact support."
            
    context = get_common_context()
    context['error_message'] = error_message
    context['success_message'] = success_message
    context['booking'] = booking
    return render(request, 'payment_success.html', context)

def payment_cancel(request):
    """Handle payment cancellation with signed token verification."""
    signed_token = request.GET.get('token')
    
    if signed_token:
        try:
            # Verify the signed token (CRIT-05)
            booking_id = booking_signer.unsign(signed_token)
            booking = Booking.objects.get(id=int(booking_id))
            
            # Only cancel if it was awaiting payment
            if booking.status == 'awaiting_payment':
                booking.status = 'canceled'
                booking.save()
                logger.info(f"Booking {booking_id} canceled by user via signed token.")
        except BadSignature:
            logger.warning(f"Invalid signed token in payment_cancel from IP: {get_client_ip(request)}")
        except Booking.DoesNotExist:
            logger.debug(f"Payment cancel for non-existent booking")
        except Exception as e:
            logger.error(f"Error in payment_cancel: {e}")

    context = get_common_context()
    return render(request, 'payment_cancel.html', context)

@login_required
def booking_receipt(request, booking_id):
    context = get_common_context()
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security check: ensure user owns this booking
    if booking.user != request.user and booking.guest_email != request.user.email:
        logger.warning(f"Unauthorized receipt access attempt: user={request.user.username}, booking={booking_id}")
        SecurityLogger.log_access_denied(request, "Attempted to access another user's booking receipt")
        raise PermissionDenied("You don't have permission to view this receipt.")
        
    # Generate PDF if it doesn't exist
    if not booking.receipt_pdf:
        try:
            generate_receipt_pdf(booking)
        except Exception as e:
            logger.error(f"Error generating receipt PDF for booking {booking_id}: {e}")
        
    context['booking'] = booking
    return render(request, 'receipt.html', context)

@login_required
def my_bookings_view(request):
    context = get_common_context()
    # Find bookings linked to user OR matching their email
    bookings = Booking.objects.filter(
        Q(user=request.user) | Q(guest_email=request.user.email)
    ).exclude(status='awaiting_payment').order_by('-check_in')
    
    context['bookings'] = bookings
    return render(request, 'my_bookings.html', context)

from django.contrib.auth import login
from .forms import SignUpForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = SignUpForm()
        context.update(get_common_context())
        return context
    
    def form_valid(self, form):
        # Log successful login
        SecurityLogger.log_login_attempt(self.request, True, form.get_user().username)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Log failed login attempt
        username = form.data.get('username', 'unknown')
        SecurityLogger.log_login_attempt(self.request, False, username)
        return super().form_invalid(form)

@rate_limit(key='signup', max_requests=5, window=300)
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            SecurityLogger.log_login_attempt(request, True, user.username)
            logger.info(f"New user registered: {user.email}")
            return redirect('homepage')
        else:
            SecurityLogger.log_login_attempt(request, False, form.data.get('email', 'unknown'))
            login_form = AuthenticationForm()
            context = get_common_context()
            context['form'] = login_form
            context['signup_form'] = form
            context['show_signup'] = True
            return render(request, 'registration/login.html', context)
    else:
        form = SignUpForm()
        login_form = AuthenticationForm()
        context = get_common_context()
        context['form'] = login_form
        context['signup_form'] = form
        context['show_signup'] = True
        return render(request, 'registration/login.html', context)

@csrf_exempt
@require_POST
@rate_limit(key='stripe_webhook', max_requests=100, window=60)
def stripe_webhook(request):
    """
    Handle Stripe webhook events securely.
    Rate limited to prevent abuse while allowing legitimate Stripe traffic.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not sig_header:
        logger.warning(f"Stripe webhook called without signature from IP: {get_client_ip(request)}")
        return HttpResponse(status=400)
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return HttpResponse(status=500)
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.warning(f"Invalid Stripe webhook payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.warning(f"Invalid Stripe webhook signature from IP: {get_client_ip(request)}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session.get('client_reference_id')
        
        if booking_id:
            try:
                booking = Booking.objects.get(id=int(booking_id))
                # Verify the Stripe session ID matches
                if booking.stripe_session_id != session.get('id'):
                    logger.warning(f"Stripe session ID mismatch for booking {booking_id}")
                    return HttpResponse(status=400)
                
                # Confirm if not already confirmed
                if booking.status == 'awaiting_payment':
                    booking.status = 'confirmed'
                    booking.save()
                    logger.info(f"Booking {booking_id} confirmed via Stripe webhook.")
                    
                # Send receipt if not already generated
                if not booking.receipt_pdf:
                    try:
                        send_receipt_email(booking)
                    except Exception as e:
                        logger.error(f"Error sending email in webhook for booking {booking_id}: {e}")
                        
            except Booking.DoesNotExist:
                logger.warning(f"Stripe webhook for non-existent booking: {booking_id}")
            except Exception as e:
                logger.error(f"Error processing Stripe webhook: {e}")

    return HttpResponse(status=200)
