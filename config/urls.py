from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve
from django.shortcuts import render, redirect
from django.http import HttpResponse
from apps.profiles import views as profile_views

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')
    return render(request, 'home.html')

urlpatterns = [
    # Administration
    path('cass/', admin.site.urls),
    
    # Home landing
    path('', home_view, name='home'),
    
    # Authentication & Accounts
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    
    # Creator Dashboard
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # Click tracking redirect
    path('l/<int:link_id>/', profile_views.link_redirect_view, name='link_redirect'),
    
    # Appearance Live Preview Frame
    path('preview/<str:username>/', profile_views.preview_profile_view, name='preview_profile'),

    # Public Creator Page Interactions
    path('<str:username>/contact.vcf', profile_views.download_vcard_view, name='download_vcard'),
    path('<str:username>/api/slots/', profile_views.get_available_slots_api, name='api_available_slots'),
    path('<str:username>/book/<int:service_id>/', profile_views.book_service_view, name='book_service'),
    path('<str:username>/contact/', profile_views.submit_contact_view, name='submit_contact'),

    # Clear Favicon Handler (prevents wildcard shadowing and 404s)
    path('favicon.ico', lambda r: HttpResponse(status=204), name='favicon'),

    # Static & Media Handlers (must precede wildcard <str:username>/ to prevent route shadowing)
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # Public Creator Profile Canonical URL
    path('<str:username>/', profile_views.public_profile_view, name='public_profile'),
]
