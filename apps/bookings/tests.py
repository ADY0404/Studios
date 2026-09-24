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

    def test_booking_request_emails_to_creator_and_visitor(self):
        from django.core import mail
        mail.outbox.clear()

        # Pick next Wednesday
        today = timezone.now().date()
        days_ahead = (2 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_wednesday = today + timedelta(days=days_ahead)

        response = self.client.post(f'/coachdan/book/{self.service.id}/', {
            'visitor_name': 'Emma Watson',
            'visitor_email': 'emma@client.com',
            'visitor_phone': '+1 555 123 4567',
            'notes': 'Looking forward to the coaching session',
            'booking_date': target_wednesday.strftime('%Y-%m-%d'),
            'booking_time': '09:00'
        })
        self.assertEqual(response.status_code, 302)

        # 2 emails must be sent: 1 alert to creator, 1 receipt to visitor
        self.assertEqual(len(mail.outbox), 2)

        recipients = [m.to[0] for m in mail.outbox]
        self.assertIn('coach@example.com', recipients)
        self.assertIn('emma@client.com', recipients)

        # Check creator email
        creator_mail = next(m for m in mail.outbox if m.to[0] == 'coach@example.com')
        self.assertIn('New Booking Request', creator_mail.subject)
        self.assertEqual(creator_mail.reply_to, ['emma@client.com'])

        # Check visitor receipt
        visitor_mail = next(m for m in mail.outbox if m.to[0] == 'emma@client.com')
        self.assertIn('Booking Request Received', visitor_mail.subject)
        self.assertEqual(visitor_mail.reply_to, ['coach@example.com'])

    def test_admin_booking_status_action_sends_email(self):
        from django.core import mail
        mail.outbox.clear()

        booking = Booking.objects.create(
            profile=self.profile,
            service=self.service,
            visitor_name='Admin Test Visitor',
            visitor_email='visitor@external.com',
            start_time=timezone.now() + timedelta(days=3),
            end_time=timezone.now() + timedelta(days=3, minutes=30),
            status='pending'
        )

        admin = User.objects.create_superuser('bossadmin', 'admin@linkstudio.app', 'SecretAdmin123!')
        self.client.force_login(admin)

        # Trigger confirm_bookings admin action
        response = self.client.post('/admin/bookings/booking/', {
            'action': 'confirm_bookings',
            '_selected_action': [booking.id]
        })
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')

        # Visitor received confirmation email from admin action
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['visitor@external.com'])
        self.assertIn('Confirmed', mail.outbox[0].subject)



