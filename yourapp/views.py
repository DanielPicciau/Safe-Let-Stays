from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
import stripe
from datetime import datetime
from .models import Property, Booking
from .forms import PropertyForm
from .utils import generate_receipt_pdf, send_receipt_email

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
    # Exclude featured from the list if desired, or just show all
    context['properties'] = properties[:3] # Show top 3 matches
    
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
def delete_property_view(request, pk):
    from django.contrib import messages
    property_obj = get_object_or_404(Property, pk=pk)
    property_title = property_obj.title
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

def create_checkout_session(request, property_id):
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, pk=property_id)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Calculate nights and get details
        checkin_str = request.POST.get('checkin')
        checkout_str = request.POST.get('checkout')
        guests = request.POST.get('guests', '1')
        nights = 1
        description_parts = []
        
        if checkin_str and checkout_str:
            try:
                checkin = datetime.strptime(checkin_str, '%Y-%m-%d')
                checkout = datetime.strptime(checkout_str, '%Y-%m-%d')
                delta = checkout - checkin
                nights = delta.days
                if nights < 1:
                    nights = 1
                
                # Format dates for description
                date_range = f"{checkin.strftime('%d %b %Y')} - {checkout.strftime('%d %b %Y')}"
                description_parts.append(date_range)
            except ValueError:
                pass
        
        description_parts.append(f"{nights} Night{'s' if nights > 1 else ''}")
        description_parts.append(f"{guests} Guest{'s' if guests != '1' else ''}")
        
        full_description = " • ".join(description_parts)
        
        # Get guest details
        if request.user.is_authenticated:
            guest_name = request.user.get_full_name() or request.user.username
            guest_email = request.user.email
            guest_phone = getattr(request.user.profile, 'phone_number', '') if hasattr(request.user, 'profile') else ''
        else:
            guest_name = request.POST.get('guest_name', 'Guest')
            guest_email = request.POST.get('guest_email', 'pending@example.com')
            guest_phone = request.POST.get('guest_phone', '')

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
                guests=int(guests),
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
                                'name': f"Stay at {property_obj.title}",
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
                    'checkin': checkin_str,
                    'checkout': checkout_str,
                    'guests': guests,
                    'nights': nights
                }
            )
            
            # Update booking with session ID
            booking.stripe_session_id = checkout_session.id
            booking.save()
            
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return redirect('homepage')

def payment_success(request):
    booking_id = request.GET.get('booking_id')
    error_message = None
    success_message = None
    
    import sys
    print(f"DEBUG: payment_success view reached. Booking ID: {booking_id}", file=sys.stderr)
    
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id)
            print(f"DEBUG: Booking found: {booking}. Status: {booking.status}", file=sys.stderr)
            
            # Only confirm if it was awaiting payment
            if booking.status == 'awaiting_payment':
                booking.status = 'confirmed'
                booking.save()
                print(f"DEBUG: Booking confirmed. Sending receipt...", file=sys.stderr)
                
                # Generate Receipt PDF and Send Email
                try:
                    send_receipt_email(booking)
                    success_message = "Receipt sent successfully!"
                except Exception as e:
                    print(f"Error sending receipt email: {e}", file=sys.stderr)
                    error_message = f"Booking confirmed, but failed to send email: {str(e)}"
            else:
                print(f"DEBUG: Booking status was not awaiting_payment. Skipping confirmation.", file=sys.stderr)
                if booking.status == 'confirmed':
                     success_message = "Booking already confirmed."
                    
        except Booking.DoesNotExist:
            print(f"DEBUG: Booking with ID {booking_id} does not exist.", file=sys.stderr)
            error_message = "Booking not found."
            pass
            
    context = get_common_context()
    context['error_message'] = error_message
    context['success_message'] = success_message
    return render(request, 'payment_success.html', context)

def payment_cancel(request):
    booking_id = request.GET.get('booking_id')
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id)
            # Only cancel if it was awaiting payment
            if booking.status == 'awaiting_payment':
                booking.status = 'canceled'
                booking.save()
        except Booking.DoesNotExist:
            pass

    context = get_common_context()
    return render(request, 'payment_cancel.html', context)

@login_required
def booking_receipt(request, booking_id):
    context = get_common_context()
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security check: ensure user owns this booking
    if booking.user != request.user and booking.guest_email != request.user.email:
        return redirect('my_bookings')
        
    # Generate PDF if it doesn't exist
    if not booking.receipt_pdf:
        try:
            generate_receipt_pdf(booking)
        except Exception as e:
            print(f"Error generating receipt PDF: {e}")
        
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

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homepage')
        else:
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
