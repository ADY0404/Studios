from django.urls import path
from apps.dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_overview, name='overview'),
    
    # Profile Details
    path('profile/', views.profile_details, name='profile'),
    
    # Links
    path('links/', views.links_manager, name='links'),
    path('links/<int:link_id>/edit/', views.edit_link, name='link_edit'),
    path('links/<int:link_id>/toggle/', views.toggle_link, name='link_toggle'),
    path('links/<int:link_id>/delete/', views.delete_link, name='link_delete'),
    path('links/<int:link_id>/up/', views.move_link_up, name='link_up'),
    path('links/<int:link_id>/down/', views.move_link_down, name='link_down'),
    path('links/api/reorder/', views.reorder_links_api, name='link_reorder_api'),
    
    # Social Media
    path('social/', views.social_manager, name='social'),
    path('social/<int:social_id>/toggle/', views.toggle_social, name='social_toggle'),
    path('social/<int:social_id>/delete/', views.delete_social, name='social_delete'),
    
    # Appearance
    path('appearance/', views.appearance_studio, name='appearance'),
    
    # Bookings
    path('bookings/', views.bookings_manager, name='bookings'),
    path('bookings/services/add/', views.add_service, name='add_service'),
    path('bookings/services/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('bookings/services/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('bookings/<int:booking_id>/status/', views.update_booking_status, name='update_booking_status'),
    path('bookings/availability/', views.update_availability, name='update_availability'),
    
    # Contacts
    path('contacts/', views.contacts_manager, name='contacts'),
    path('contacts/export/', views.export_contacts_csv, name='export_contacts'),
    path('contacts/<int:contact_id>/delete/', views.delete_contact, name='delete_contact'),
]
