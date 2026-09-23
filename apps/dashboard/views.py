import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.profiles.models import Profile, Appearance
from apps.profiles.forms import ProfileForm, AppearanceForm
from apps.links.models import Link
from apps.links.forms import LinkForm
from apps.social.models import SocialAccount
from apps.social.forms import SocialAccountForm
from apps.bookings.models import Service, AvailabilityRule, Booking
from apps.bookings.forms import ServiceForm, AvailabilityRuleForm
from apps.contacts.models import ContactSubmission

@login_required
def dashboard_overview(request):
    profile = request.user.profile
    links = profile.links.all()
    total_clicks = sum(link.click_count for link in links)
    
    upcoming_bookings = profile.bookings.filter(
        start_time__gte=timezone.now()
    ).select_related('service').order_by('start_time')[:5]
    
    recent_contacts = profile.contacts.all()[:5]

    context = {
        'profile': profile,
        'links_count': links.count(),
        'total_clicks': total_clicks,
        'upcoming_bookings_count': profile.bookings.filter(start_time__gte=timezone.now(), status__in=['pending', 'confirmed']).count(),
        'contacts_count': profile.contacts.count(),
        'upcoming_bookings': upcoming_bookings,
        'recent_contacts': recent_contacts,
    }
    return render(request, 'dashboard/overview.html', context)


# ==============================
# LINKS MANAGEMENT
# ==============================
@login_required
def links_manager(request):
    profile = request.user.profile
    links = profile.links.all().order_by('order', '-created_at')
    
    if request.method == 'POST':
        form = LinkForm(request.POST, request.FILES)
        if form.is_valid():
            new_link = form.save(commit=False)
            new_link.profile = profile
            # Put new link at the end of the order
            max_order = links.last().order if links.exists() else 0
            new_link.order = max_order + 1
            new_link.save()
            messages.success(request, f"Link '{new_link.title}' created successfully!")
            return redirect('dashboard:links')
    else:
        form = LinkForm()

    return render(request, 'dashboard/links.html', {
        'profile': profile,
        'links': links,
        'form': form
    })


@login_required
def edit_link(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    
    if request.method == 'POST':
        form = LinkForm(request.POST, request.FILES, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, f"Link '{link.title}' updated!")
            return redirect('dashboard:links')
    else:
        form = LinkForm(instance=link)

    return render(request, 'dashboard/link_edit.html', {
        'profile': profile,
        'link': link,
        'form': form
    })


@login_required
@require_POST
def toggle_link(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    link.is_active = not link.is_active
    link.save(update_fields=['is_active'])
    status_str = "enabled" if link.is_active else "disabled"
    messages.info(request, f"Link '{link.title}' {status_str}.")
    return redirect('dashboard:links')


@login_required
@require_POST
def delete_link(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    title = link.title
    link.delete()
    messages.success(request, f"Link '{title}' was deleted.")
    return redirect('dashboard:links')


@login_required
@require_POST
def move_link_up(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    prev_link = profile.links.filter(order__lt=link.order).order_by('-order').first()
    if prev_link:
        link.order, prev_link.order = prev_link.order, link.order
        Link.objects.bulk_update([link, prev_link], ['order'])
    return redirect('dashboard:links')


@login_required
@require_POST
def move_link_down(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    next_link = profile.links.filter(order__gt=link.order).order_by('order').first()
    if next_link:
        link.order, next_link.order = next_link.order, link.order
        Link.objects.bulk_update([link, next_link], ['order'])
    return redirect('dashboard:links')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_links_api(request):
    """
    Accepts JSON payload: { 'order': [id1, id2, id3, ...] }
    and updates the position index cleanly without duplicates.
    """
    profile = request.user.profile
    order_ids = request.data.get('order', [])
    
    if not isinstance(order_ids, list):
        return Response({'error': 'Invalid format. Array of IDs expected.'}, status=400)

    # Fetch user's links
    user_links = {link.id: link for link in profile.links.filter(id__in=order_ids)}
    
    updates = []
    for index, link_id in enumerate(order_ids):
        try:
            link_id_int = int(link_id)
        except (ValueError, TypeError):
            continue
        if link_id_int in user_links:
            link = user_links[link_id_int]
            link.order = index
            updates.append(link)

    if updates:
        Link.objects.bulk_update(updates, ['order'])

    return Response({'status': 'success', 'updated_count': len(updates)})


# ==============================
# SOCIAL MEDIA MANAGEMENT
# ==============================
@login_required
def social_manager(request):
    profile = request.user.profile
    socials = profile.social_accounts.all().order_by('order', 'platform')

    if request.method == 'POST':
        form = SocialAccountForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data['platform']
            # Update existing or create new
            account, created = SocialAccount.objects.update_or_create(
                profile=profile,
                platform=platform,
                defaults={
                    'url': form.cleaned_data['url'],
                    'is_active': form.cleaned_data['is_active']
                }
            )
            msg = f"{account.get_platform_display()} added!" if created else f"{account.get_platform_display()} updated!"
            messages.success(request, msg)
            return redirect('dashboard:social')
    else:
        form = SocialAccountForm()

    return render(request, 'dashboard/social.html', {
        'profile': profile,
        'socials': socials,
        'form': form
    })


@login_required
@require_POST
def delete_social(request, social_id):
    profile = request.user.profile
    account = get_object_or_404(SocialAccount, id=social_id, profile=profile)
    name = account.get_platform_display()
    account.delete()
    messages.success(request, f"{name} profile removed.")
    return redirect('dashboard:social')


@login_required
@require_POST
def toggle_social(request, social_id):
    profile = request.user.profile
    account = get_object_or_404(SocialAccount, id=social_id, profile=profile)
    account.is_active = not account.is_active
    account.save(update_fields=['is_active'])
    status_str = "enabled" if account.is_active else "disabled"
    messages.info(request, f"{account.get_platform_display()} {status_str}.")
    return redirect('dashboard:social')


# ==============================
# APPEARANCE STUDIO
# ==============================
@login_required
def appearance_studio(request):
    profile = request.user.profile
    appearance, _ = Appearance.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        form = AppearanceForm(request.POST, request.FILES, instance=appearance)
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Determine bg_type based on file upload / clear actions
            new_image_uploaded = 'bg_image' in request.FILES and request.FILES['bg_image']
            image_cleared = request.POST.get('bg_image-clear') or request.POST.get('clear_bg_image') == 'true'

            if new_image_uploaded:
                # New image uploaded — force bg_type to 'image'
                app_obj.bg_type = 'image'
            elif image_cleared:
                # Image cleared — revert bg_type to the selected type (gradient/color)
                # Manually delete existing image if still set on the instance
                if appearance.bg_image:
                    appearance.bg_image.delete(save=False)
                app_obj.bg_image = None
                if app_obj.bg_type == 'image':
                    app_obj.bg_type = 'gradient'

            app_obj.save()
            messages.success(request, 'Appearance saved! Your profile is updated.')
            return redirect('dashboard:appearance')
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    field_name = 'General' if field == '__all__' else field.replace('_', ' ').capitalize()
                    messages.error(request, f"{field_name}: {err}")
    else:
        form = AppearanceForm(instance=appearance)

    return render(request, 'dashboard/appearance.html', {
        'profile': profile,
        'appearance': appearance,
        'form': form
    })



# ==============================
# BOOKING SYSTEM MANAGEMENT
# ==============================
@login_required
def bookings_manager(request):
    profile = request.user.profile
    status_filter = request.GET.get('status', 'all')
    
    bookings_qs = profile.bookings.select_related('service').order_by('-start_time')
    if status_filter != 'all' and status_filter in dict(Booking.STATUS_CHOICES):
        bookings_qs = bookings_qs.filter(status=status_filter)
        
    services = profile.services.all().order_by('order', 'price')
    availability_rules = profile.availability_rules.all().order_by('day_of_week')
    
    service_form = ServiceForm()

    return render(request, 'dashboard/bookings.html', {
        'profile': profile,
        'bookings': bookings_qs,
        'services': services,
        'rules': availability_rules,
        'service_form': service_form,
        'current_status': status_filter,
    })


@login_required
@require_POST
def add_service(request):
    profile = request.user.profile
    form = ServiceForm(request.POST)
    if form.is_valid():
        service = form.save(commit=False)
        service.profile = profile
        service.save()
        messages.success(request, f"Service '{service.title}' created!")
    else:
        messages.error(request, "Failed to create service. Check the form fields.")
    return redirect('dashboard:bookings')


@login_required
def edit_service(request, service_id):
    profile = request.user.profile
    service = get_object_or_404(Service, id=service_id, profile=profile)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Service '{service.title}' updated.")
            return redirect('dashboard:bookings')
    else:
        form = ServiceForm(instance=service)
        
    return render(request, 'dashboard/service_edit.html', {
        'profile': profile,
        'service': service,
        'form': form
    })


@login_required
@require_POST
def delete_service(request, service_id):
    profile = request.user.profile
    service = get_object_or_404(Service, id=service_id, profile=profile)
    title = service.title
    service.delete()
    messages.success(request, f"Service '{title}' was deleted.")
    return redirect('dashboard:bookings')


@login_required
@require_POST
def update_booking_status(request, booking_id):
    profile = request.user.profile
    booking = get_object_or_404(Booking, id=booking_id, profile=profile)
    new_status = request.POST.get('status')
    
    if new_status in dict(Booking.STATUS_CHOICES):
        booking.status = new_status
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Booking for {booking.visitor_name} marked as {booking.get_status_display()}.")
    return redirect('dashboard:bookings')


@login_required
def update_availability(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        for day in range(7):
            start = request.POST.get(f'start_{day}')
            end = request.POST.get(f'end_{day}')
            active = request.POST.get(f'active_{day}') == 'on'
            
            if start and end:
                AvailabilityRule.objects.update_or_create(
                    profile=profile,
                    day_of_week=day,
                    defaults={
                        'start_time': start,
                        'end_time': end,
                        'is_active': active
                    }
                )
        messages.success(request, "Availability hours updated successfully.")
        return redirect('dashboard:bookings')

    return redirect('dashboard:bookings')


# ==============================
# CONTACTS MANAGEMENT
# ==============================
@login_required
def contacts_manager(request):
    profile = request.user.profile
    query = request.GET.get('q', '').strip()
    
    contacts = profile.contacts.all().order_by('-created_at')
    if query:
        contacts = contacts.filter(name__icontains=query) | contacts.filter(email__icontains=query)

    return render(request, 'dashboard/contacts.html', {
        'profile': profile,
        'contacts': contacts,
        'query': query
    })


@login_required
def export_contacts_csv(request):
    profile = request.user.profile
    contacts = profile.contacts.all().order_by('-created_at')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{profile.username}_contacts.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Message', 'Date Submitted'])
    
    for c in contacts:
        writer.writerow([
            c.name,
            c.email,
            c.phone,
            c.message,
            c.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    return response


@login_required
@require_POST
def delete_contact(request, contact_id):
    profile = request.user.profile
    contact = get_object_or_404(ContactSubmission, id=contact_id, profile=profile)
    name = contact.name
    contact.delete()
    messages.success(request, f"Contact record for '{name}' was deleted.")
    return redirect('dashboard:contacts')


# ==============================
# PROFILE DETAILS
# ==============================
@login_required
def profile_details(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Creator profile updated successfully!")
            return redirect('dashboard:profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'dashboard/profile.html', {
        'profile': profile,
        'form': form
    })
