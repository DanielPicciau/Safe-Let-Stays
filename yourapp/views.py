from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.exceptions import PermissionDenied
from django.utils.html import escape
import stripe
import logging
from datetime import datetime
from .models import Property, Booking
from .forms import PropertyForm, CheckoutForm
from .utils import generate_receipt_pdf, send_receipt_email
from .security import rate_limit, get_client_ip, InputValidator, SecurityLogger

logger = logging.getLogger(__name__)


def csrf_failure(request, reason=""):
    """Custom CSRF failure view."""
    logger.warning(f"CSRF failure: {reason} from IP: {get_client_ip(request)}")
    return HttpResponseForbidden(
        "Security validation failed. Please refresh the page and try again."
    )

def get_common_context():
    return {
        'site_name': 'Safe Let Stays',
        'brand_color': '#2E7D32',
        'contact_phone': '+44 114 123 4567',
        'contact_email': 'hello@safeletstays.co.uk',
        'business_address': '123 Sheffield Street, Sheffield, S1 1AA',
    }

def homepage(request):
    """Render the homepage with database context data."""
    context = get_common_context()
    
    properties = Property.objects.all()
        
    # Featured Property
    featured = Property.objects.filter(is_featured=True).first()
    if not featured and properties.exists():
        featured = properties.first()
        
    context['featured_property'] = featured
    
    # Top Properties for homepage section (selected by staff)
    top_properties = Property.objects.filter(show_on_homepage=True).order_by('homepage_order')[:3]
    if top_properties.count() < 3:
        # Fallback to first 3 properties if not enough are selected
        top_properties = properties[:3]
    context['top_properties'] = top_properties
    
    return render(request, 'homepage.html', context)

def properties_view(request):
    context = get_common_context()
    properties = Property.objects.all()
    
    # Search Logic
    guests = request.GET.get('guests')
    beds = request.GET.get('beds')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if guests:
        try:
            properties = properties.filter(capacity__gte=int(guests))
        except ValueError:
            pass
            
    if beds:
        try:
            if beds == '4':
                properties = properties.filter(beds__gte=4)
            else:
                properties = properties.filter(beds=int(beds))
        except ValueError:
            pass
            
    context['properties'] = properties
    context['search_params'] = {
        'guests': guests,
        'beds': beds,
        'check_in': check_in,
        'check_out': check_out,
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
    similar_properties = Property.objects.filter(beds=property_obj.beds).exclude(pk=property_obj.pk)[:3]
    if similar_properties.count() < 3:
        # Fill with other properties if not enough similar ones
        additional = Property.objects.exclude(pk=property_obj.pk).exclude(pk__in=similar_properties)[:3-similar_properties.count()]
        similar_properties = list(similar_properties) + list(additional)
    
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
            form.save()
            return redirect('staff_panel')
        else:
            print("Form errors:", form.errors)
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
            return redirect('staff_panel')
        else:
            print("Edit Form errors:", form.errors)
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
    
    # Format dates for description
    date_range = f"{checkin.strftime('%d %b %Y')} - {checkout.strftime('%d %b %Y')}"
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
        guest_email = form.cleaned_data.get('guest_email') or 'pending@example.com'
        guest_phone = form.cleaned_data.get('guest_phone') or ''

    try:
        # Create pending booking
        booking = Booking.objects.create(
            property=property_obj,
            user=request.user if request.user.is_authenticated else None,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            check_in=checkin,
            check_out=checkout,
            guests=guests,
            total_price=property_obj.price_from * nights,
            status='awaiting_payment'
        )

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
                            'name': f"Stay at {escape(property_obj.title)}",
                            'description': full_description,
                            'images': images,
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/payment-success/') + f"?booking_id={booking.id}",
            cancel_url=request.build_absolute_uri('/payment-cancel/') + f"?booking_id={booking.id}",
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
    booking_id = request.GET.get('booking_id')
    error_message = None
    success_message = None
    
    logger.debug(f"payment_success view reached. Booking ID: {booking_id}")
    
    if booking_id:
        # Validate booking_id is a valid integer
        if not InputValidator.validate_positive_integer(booking_id):
            logger.warning(f"Invalid booking_id format: {booking_id} from IP: {get_client_ip(request)}")
            error_message = "Invalid booking reference."
        else:
            try:
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
                            error_message = f"Booking confirmed, but failed to send email. Please contact support."
                         
            except Booking.DoesNotExist:
                logger.warning(f"Payment success with non-existent booking: {booking_id}")
                # Don't reveal if booking exists or not
                error_message = "Unable to process request. Please contact support."
            except Exception as e:
                logger.error(f"Error in payment_success view: {e}")
                error_message = "An error occurred. Please contact support."
            
    context = get_common_context()
    context['error_message'] = error_message
    context['success_message'] = success_message
    return render(request, 'payment_success.html', context)

def payment_cancel(request):
    booking_id = request.GET.get('booking_id')
    if booking_id and InputValidator.validate_positive_integer(booking_id):
        try:
            booking = Booking.objects.get(id=int(booking_id))
            # Only cancel if it was awaiting payment
            if booking.status == 'awaiting_payment':
                booking.status = 'canceled'
                booking.save()
                logger.info(f"Booking {booking_id} canceled by user.")
        except Booking.DoesNotExist:
            pass
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
def stripe_webhook(request):
    """
    Handle Stripe webhook events securely.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not sig_header:
        logger.warning(f"Stripe webhook called without signature from IP: {get_client_ip(request)}")
        return HttpResponse(status=400)
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return HttpResponse(status=500)
    
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
