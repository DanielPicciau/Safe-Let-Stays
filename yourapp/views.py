from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Property
from .forms import PropertyForm

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

def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('staff_panel')
    else:
        form = PropertyForm()
    return render(request, 'staff/property_form.html', {'form': form, 'title': 'Add Property'})

def edit_property_view(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            return redirect('staff_panel')
    else:
        form = PropertyForm(instance=property_obj)
    return render(request, 'staff/property_form.html', {'form': form, 'title': 'Edit Property'})

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
