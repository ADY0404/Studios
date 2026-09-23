from django.shortcuts import redirect
from django.contrib import messages

class CreatorRequiredMiddleware:
    """
    Ensures administrator accounts (staff / superuser) cannot access creator dashboard pages.
    The admin console strictly uses the default Django Admin (/admin/).
    Creators manage their bio pages via /dashboard/.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/dashboard/'):
            if request.user.is_authenticated:
                if request.user.is_staff or request.user.is_superuser:
                    messages.warning(
                        request, 
                        "Administrators manage LinkStudio via the Django Admin Console (/admin/) and do not have access to creator pages."
                    )
                    return redirect('/admin/')
                if not hasattr(request.user, 'profile'):
                    messages.error(request, "Creator profile not found. Please contact support.")
                    return redirect('accounts:logout')
                    
        return self.get_response(request)

