from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.db.models import F
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.core.exceptions import ValidationError

from apps.profiles.models import Profile, Appearance
from apps.links.models import Link
from apps.bookings.models import Service, Booking
from apps.bookings.services import get_available_slots, reserve_booking
from apps.bookings.forms import BookingRequestForm
from apps.contacts.models import ContactSubmission
from apps.contacts.forms import ContactSubmissionForm
from apps.contacts.vcard import generate_vcard_content

def public_profile_view(request, username):
    """
    Renders the public creator link-in-bio page.
    Clean canonical URL: /<username>/
    """
    profile = get_object_or_404(
        Profile.objects.select_related('appearance', 'user'), 
        username__iexact=username, 
        is_public=True,
        user__is_staff=False,
        user__is_superuser=False
    )

    # Increment view count atomically
    Profile.objects.filter(pk=profile.pk).update(total_views=F('total_views') + 1)

    # Fetch active links and social accounts
    links = profile.links.filter(is_active=True).order_by('order')
    socials = profile.social_accounts.filter(is_active=True).order_by('order')
    services = profile.services.filter(is_active=True).order_by('order')

    # Safely get or create appearance
    appearance, _ = Appearance.objects.get_or_create(profile=profile)

    contact_form = ContactSubmissionForm() if profile.show_contact_form else None

    return render(request, 'public/creator_profile.html', {
        'profile': profile,
        'appearance': appearance,
        'links': links,
        'socials': socials,
        'services': services,
        'contact_form': contact_form,
        'is_preview': False,
    })


@xframe_options_sameorigin
def preview_profile_view(request, username):
    """
    Renders live preview inside the Appearance Studio iframe.
    @xframe_options_sameorigin allows this page to be embedded in an iframe
    on the same origin (the dashboard) without triggering X-Frame-Options DENY.
    """
    profile = get_object_or_404(
        Profile.objects.select_related('appearance', 'user'), 
        username__iexact=username,
        user__is_staff=False,
        user__is_superuser=False
    )
    links = profile.links.filter(is_active=True).order_by('order')
    socials = profile.social_accounts.filter(is_active=True).order_by('order')
    services = profile.services.filter(is_active=True).order_by('order')
    # Safely get or create appearance
    appearance, _ = Appearance.objects.get_or_create(profile=profile)

    contact_form = ContactSubmissionForm() if profile.show_contact_form else None

    return render(request, 'public/creator_profile.html', {
        'profile': profile,
        'appearance': appearance,
        'links': links,
        'socials': socials,
        'services': services,
        'contact_form': contact_form,
        'is_preview': True,
    })


def link_redirect_view(request, link_id):
    """
    Tracks click count atomically and redirects to target URL.
    """
    link = get_object_or_404(Link, id=link_id, is_active=True)
    Link.objects.filter(pk=link.pk).update(click_count=F('click_count') + 1)
    return redirect(link.url)


def download_vcard_view(request, username):
    """
    Generates and returns standard .vcf vCard file for mobile contact save.
    """
    profile = get_object_or_404(Profile, username__iexact=username, is_public=True)
    if not profile.show_save_contact:
        raise Http404("Contact card is disabled by creator.")

    vcf_content = generate_vcard_content(profile, request=request)
    response = HttpResponse(vcf_content, content_type='text/vcard; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{profile.username}.vcf"'
    return response


def get_available_slots_api(request, username):
    """
    API returning available booking slots for a given service and date.
    Query params: service_id, date (YYYY-MM-DD)
    """
    profile = get_object_or_404(Profile, username__iexact=username)
    service_id = request.GET.get('service_id')
    date_str = request.GET.get('date')

    if not service_id or not date_str:
        return JsonResponse({'error': 'service_id and date are required.'}, status=400)

    service = get_object_or_404(Service, id=service_id, profile=profile, is_active=True)

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    slots = get_available_slots(profile, service, target_date)
    return JsonResponse({'slots': slots, 'service': service.title, 'date': date_str})


@require_POST
def book_service_view(request, username, service_id):
    """
    Submits booking request with atomic double-booking prevention.
    """
    profile = get_object_or_404(Profile, username__iexact=username, is_public=True)
    service = get_object_or_404(Service, id=service_id, profile=profile, is_active=True)
    form = BookingRequestForm(request.POST)

    if form.is_valid():
        booking_date = form.cleaned_data['booking_date']
        booking_time_str = form.cleaned_data['booking_time']
        
        try:
            time_part = datetime.strptime(booking_time_str, '%H:%M').time()
            naive_dt = datetime.combine(booking_date, time_part)
            slot_start_dt = timezone.make_aware(naive_dt)
        except Exception:
            messages.error(request, "Invalid time format chosen.")
            return redirect('public_profile', username=username)

        try:
            booking = reserve_booking(
                profile=profile,
                service=service,
                visitor_name=form.cleaned_data['visitor_name'],
                visitor_email=form.cleaned_data['visitor_email'],
                visitor_phone=form.cleaned_data['visitor_phone'],
                notes=form.cleaned_data['notes'],
                slot_start_dt=slot_start_dt
            )
            messages.success(
                request, 
                f"Booking requested successfully for {service.title} on {booking_date.strftime('%b %d, %Y')} at {booking_time_str}! {profile.display_name} will confirm shortly."
            )
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
    else:
        messages.error(request, "Please check the booking form fields and choose an available time.")

    return redirect('public_profile', username=username)


@require_POST
def submit_contact_view(request, username):
    """
    Saves voluntary visitor contact submissions.
    """
    profile = get_object_or_404(Profile, username__iexact=username, is_public=True)
    if not profile.show_contact_form:
        raise Http404("Contact form disabled.")

    form = ContactSubmissionForm(request.POST)
    if form.is_valid():
        submission = form.save(commit=False)
        submission.profile = profile
        submission.save()
        messages.success(request, f"Thanks for getting in touch! Your message was sent to {profile.display_name}.")
    else:
        messages.error(request, "Please fill in all required contact fields properly.")

    return redirect('public_profile', username=username)
