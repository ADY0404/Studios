from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def dashboard_overview(request):
    profile = request.user.profile
    links = list(profile.links.all())
    total_clicks = sum(link.click_count for link in links)
    
    upcoming_bookings = profile.bookings.filter(
        start_time__gte=timezone.now()
    ).select_related('service').order_by('start_time')[:5]
    
    recent_contacts = profile.contacts.all()[:5]

    context = {
        'profile': profile,
        'links_count': len(links),
        'total_clicks': total_clicks,
        'upcoming_bookings_count': profile.bookings.filter(start_time__gte=timezone.now(), status__in=['pending', 'confirmed']).count(),
        'contacts_count': profile.contacts.count(),
        'upcoming_bookings': upcoming_bookings,
        'recent_contacts': recent_contacts,
    }
    return render(request, 'dashboard/overview.html', context)

