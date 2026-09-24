from django.shortcuts import redirect
from django.contrib import messages

from apps.profiles.models import Profile, Appearance

class CreatorRequiredMiddleware:
    """
    Ensures any authenticated user (creators and administrators) accessing
    dashboard routes has a valid Profile and Appearance instance provisioned.
    Administrators have full access to both /cass/ and /dashboard/.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/dashboard/'):
            if request.user.is_authenticated:
                if not hasattr(request.user, 'profile'):
                    # Auto-provision profile for admin / staff accounts
                    base_username = request.user.username.lower().strip()
                    username = base_username
                    counter = 1
                    while Profile.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1
                    display_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                    profile = Profile.objects.create(
                        user=request.user,
                        username=username,
                        display_name=display_name,
                        public_email=request.user.email
                    )
                    Appearance.objects.get_or_create(profile=profile)
                    
        return self.get_response(request)

