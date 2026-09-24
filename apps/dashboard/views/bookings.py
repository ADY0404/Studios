from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from apps.bookings.models import Service, AvailabilityRule, Booking
from apps.bookings.forms import ServiceForm
from apps.bookings.emails import send_booking_status_update_email


@login_required
def bookings_manager(request):
    profile = request.user.profile
    status_filter = request.GET.get('status', 'all')
    
    bookings_qs = profile.bookings.select_related('service').order_by('-start_time')
    if status_filter != 'all' and status_filter in dict(Booking.STATUS_CHOICES):
        bookings_qs = bookings_qs.filter(status=status_filter)

    paginator = Paginator(bookings_qs, 25)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
        
    services = profile.services.all().order_by('order', 'price')
    availability_rules = profile.availability_rules.all().order_by('day_of_week')
    
    service_form = ServiceForm()

    return render(request, 'dashboard/bookings.html', {
        'profile': profile,
        'bookings': bookings,
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
    
    if new_status not in dict(Booking.STATUS_CHOICES):
        messages.error(request, "Invalid booking status.")
        return redirect('dashboard:bookings')

    # FIX: Enforce booking state machine transitions
    if not booking.can_transition_to(new_status):
        target_display = dict(Booking.STATUS_CHOICES).get(new_status, new_status)
        messages.error(
            request, 
            f"Cannot change booking status from '{booking.get_status_display()}' to '{target_display}'."
        )
        return redirect('dashboard:bookings')

    booking.status = new_status
    booking.save(update_fields=['status', 'updated_at'])
    send_booking_status_update_email(booking)
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

