from datetime import datetime, timedelta, time
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.bookings.models import AvailabilityRule, Booking

def get_available_slots(profile, service, target_date):
    """
    Returns a list of available datetime strings ('HH:MM') for the given profile, 
    service duration, and calendar date.
    """
    now = timezone.now()
    
    # 1. Check weekday availability rule
    weekday = target_date.weekday()
    rule = AvailabilityRule.objects.filter(profile=profile, day_of_week=weekday, is_active=True).first()
    if not rule:
        # Default fallback: Mon-Fri 09:00 to 17:00 if no custom rule exists yet
        if weekday < 5:
            rule_start = time(9, 0)
            rule_end = time(17, 0)
        else:
            return []
    else:
        rule_start = rule.start_time
        rule_end = rule.end_time

    duration = timedelta(minutes=service.duration_minutes)
    
    # Generate slots
    slots = []
    current_dt = timezone.make_aware(datetime.combine(target_date, rule_start))
    end_dt = timezone.make_aware(datetime.combine(target_date, rule_end))
    
    # Fetch existing active bookings for this profile on this date
    day_start = timezone.make_aware(datetime.combine(target_date, time.min))
    day_end = timezone.make_aware(datetime.combine(target_date, time.max))
    
    existing_bookings = list(Booking.objects.filter(
        profile=profile,
        status__in=['pending', 'confirmed'],
        start_time__lt=day_end,
        end_time__gt=day_start
    ).values('start_time', 'end_time'))

    while current_dt + duration <= end_dt:
        slot_start = current_dt
        slot_end = current_dt + duration
        
        # Ensure slot is in the future
        if slot_start > now:
            # Check overlap against all existing bookings
            is_overlap = any(
                b['start_time'] < slot_end and b['end_time'] > slot_start
                for b in existing_bookings
            )
            if not is_overlap:
                slots.append(slot_start.strftime('%H:%M'))
                
        current_dt += duration

    return slots


# FIX / CONCURRENCY NOTE:
# select_for_update() is a no-op on SQLite backend (Django ignores it or logs a warning without acquiring row locks).
# Therefore, the atomic double-booking prevention guard is only strictly enforced under production backends like MySQL/MariaDB.
# When running locally with DB_ENGINE=sqlite, concurrency tests cannot guarantee lock exclusivity.
@transaction.atomic
def reserve_booking(profile, service, visitor_name, visitor_email, visitor_phone, notes, slot_start_dt):
    """
    Atomically checks availability and creates a booking, guaranteeing double-booking prevention.
    """
    slot_end_dt = slot_start_dt + timedelta(minutes=service.duration_minutes)
    
    # Atomic lock check against existing bookings for this creator
    overlapping = Booking.objects.select_for_update().filter(
        profile=profile,
        status__in=['pending', 'confirmed'],
        start_time__lt=slot_end_dt,
        end_time__gt=slot_start_dt
    ).exists()
    
    if overlapping:
        raise ValidationError("This time slot has just been reserved. Please choose another time.")
        
    booking = Booking.objects.create(
        profile=profile,
        service=service,
        visitor_name=visitor_name,
        visitor_email=visitor_email,
        visitor_phone=visitor_phone,
        notes=notes,
        start_time=slot_start_dt,
        end_time=slot_end_dt,
        status='pending',
        payment_status='unpaid' if service.price > 0 else 'waived'
    )
    return booking
