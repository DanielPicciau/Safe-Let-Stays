from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from yourapp import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('properties/', views.properties_view, name='properties'),
    path('property/<slug:slug>/', views.property_detail_view, name='property_detail'),
    path('hosts/', views.hosts_view, name='hosts'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('about/', views.about_view, name='about'),
    
    # Staff Panel
    path('staff/', views.staff_panel_view, name='staff_panel'),
    path('staff/add/', views.add_property_view, name='add_property'),
    path('staff/edit/<int:pk>/', views.edit_property_view, name='edit_property'),
    path('staff/delete/<int:pk>/', views.delete_property_view, name='delete_property'),
    
    # =========================================================================
    # GUESTY API ENDPOINTS (Uncomment when ready to use)
    # =========================================================================
    # These endpoints provide availability data from Guesty
    # 
    # path('api/properties/<int:property_id>/availability/', 
    #      views.api_property_availability, 
    #      name='api_property_availability'),
    # 
    # path('api/properties/<int:property_id>/check-availability/', 
    #      views.api_check_availability, 
    #      name='api_check_availability'),
    # 
    # path('api/webhooks/guesty/', 
    #      views.guesty_webhook, 
    #      name='guesty_webhook'),
    # =========================================================================
    
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
