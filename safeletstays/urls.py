from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from yourapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('', views.homepage, name='homepage'),
    path('properties/', views.properties_view, name='properties'),
    path('property/<slug:slug>/', views.property_detail_view, name='property_detail'),
    path('hosts/', views.hosts_view, name='hosts'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('about/', views.about_view, name='about'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('receipt/<int:booking_id>/', views.booking_receipt, name='booking_receipt'),
    
    # Staff Panel
    path('staff/', views.staff_panel_view, name='staff_panel'),
    path('staff/add/', views.add_property_view, name='add_property'),
    path('staff/edit/<int:pk>/', views.edit_property_view, name='edit_property'),
    path('staff/delete/<int:pk>/', views.delete_property_view, name='delete_property'),
    
    # Stripe Payment
    path('create-checkout-session/<int:property_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
