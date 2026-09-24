from datetime import date, time, timedelta, datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apps.bookings.models import Service, AvailabilityRule, Booking
from apps.bookings.services import get_available_slots, reserve_booking

class BookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='coachdan', email='coach@example.com', password='Password123!')
        self.profile = self.user.profile
        self.service = Service.objects.create(
            profile=self.profile,
            title='1-on-1 Consultation',
            duration_minutes=30,
            price=50.00
        )
        # Configure Wednesday availability 09:00 - 11:00 (4 slots: 09:00, 09:30, 10:00, 10:30)
        # Wednesday is weekday 2
        AvailabilityRule.objects.create(
            profile=self.profile,
            day_of_week=2,
            start_time=time(9, 0),
            end_time=time(11, 0),
            is_active=True
        )

    def test_available_slots_calculation(self):
        # Pick next Wednesday
        today = timezone.now().date()
        days_ahead = (2 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_wednesday = today + timedelta(days=days_ahead)

        slots = get_available_slots(self.profile, self.service, target_wednesday)
        self.assertIn('09:00', slots)
        self.assertIn('09:30', slots)
        self.assertIn('10:00', slots)
        self.assertIn('10:30', slots)
        self.assertEqual(len(slots), 4)

    def test_double_booking_prevention(self):
        # Pick next Wednesday at 09:00
        today = timezone.now().date()
        days_ahead = (2 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_wednesday = today + timedelta(days=days_ahead)
        slot_start_dt = timezone.make_aware(datetime.combine(target_wednesday, time(9, 0)))

        # 1. First booking succeeds
        booking1 = reserve_booking(
            profile=self.profile,
            service=self.service,
            visitor_name='Alice Smith',
            visitor_email='alice@example.com',
            visitor_phone='123456',
            notes='Initial audit',
            slot_start_dt=slot_start_dt
        )
        self.assertIsNotNone(booking1.id)
        self.assertEqual(booking1.status, 'pending')

        # 2. Second booking at the EXACT SAME slot must fail with ValidationError
        with self.assertRaises(ValidationError):
            reserve_booking(
                profile=self.profile,
                service=self.service,
                visitor_name='Bob Brown',
                visitor_email='bob@example.com',
                visitor_phone='987654',
                notes='Also wants this slot',
                slot_start_dt=slot_start_dt
            )

        # 3. Verify slot 09:00 is now removed from available slots list
        available = get_available_slots(self.profile, self.service, target_wednesday)
        self.assertNotIn('09:00', available)
        self.assertIn('09:30', available)

    def test_booking_state_machine_transitions(self):
        booking = Booking.objects.create(
            profile=self.profile,
            service=self.service,
            visitor_name='Sam Test',
            visitor_email='sam@example.com',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
            status='pending'
        )
        # Valid transitions from pending
        self.assertTrue(booking.can_transition_to('confirmed'))
        self.assertTrue(booking.can_transition_to('rejected'))
        self.assertTrue(booking.can_transition_to('cancelled'))
        # Invalid direct transitions from pending
        self.assertFalse(booking.can_transition_to('completed'))

        # Move to confirmed
        booking.status = 'confirmed'
        self.assertTrue(booking.can_transition_to('completed'))
        self.assertTrue(booking.can_transition_to('cancelled'))
        self.assertFalse(booking.can_transition_to('pending'))
        self.assertFalse(booking.can_transition_to('rejected'))

        # Terminal state: completed
        booking.status = 'completed'
        self.assertFalse(booking.can_transition_to('pending'))
        self.assertFalse(booking.can_transition_to('confirmed'))
        self.assertFalse(booking.can_transition_to('cancelled'))

        # Terminal state: cancelled
        booking.status = 'cancelled'
        self.assertFalse(booking.can_transition_to('confirmed'))

    def test_update_booking_status_view_transition_enforcement(self):
        booking = Booking.objects.create(
            profile=self.profile,
            service=self.service,
            visitor_name='Jane Test',
            visitor_email='jane@example.com',
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, minutes=30),
            status='pending'
        )
        self.client.force_login(self.user)

        # 1. Invalid transition: pending -> completed
        resp = self.client.post(f'/dashboard/bookings/{booking.id}/status/', {'status': 'completed'})
        self.assertEqual(resp.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'pending')

        # 2. Valid transition: pending -> confirmed
        from django.core import mail
        resp = self.client.post(f'/dashboard/bookings/{booking.id}/status/', {'status': 'confirmed'})
        self.assertEqual(resp.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        self.assertTrue(len(mail.outbox) > 0)
        self.assertEqual(mail.outbox[-1].to, ['jane@example.com'])
        self.assertIn('Confirmed', mail.outbox[-1].subject)

        # 3. Invalid transition from confirmed: confirmed -> pending
        resp = self.client.post(f'/dashboard/bookings/{booking.id}/status/', {'status': 'pending'})
        self.assertEqual(resp.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')


