import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import json
from datetime import date, timedelta
from django.test import Client
from django.contrib.auth.models import User
from apps.profiles.models import Profile, Appearance
from apps.links.models import Link
from apps.social.models import SocialAccount
from apps.bookings.models import Service, AvailabilityRule, Booking
from apps.contacts.models import ContactSubmission

def run():
    client = Client()

    print('=== 1. TEST AUTHENTICATION & REGISTRATION ===')
    res = client.get('/')
    assert res.status_code == 200, f'Home failed: {res.status_code}'

    # Reserved username check
    res = client.post('/auth/register/', {
        'username': 'admin',
        'display_name': 'Fake Admin',
        'email': 'admin2@example.com',
        'password1': 'StrongPass123!',
        'password2': 'StrongPass123!'
    })
    assert res.status_code == 200 and 'reserved' in res.content.decode().lower(), 'Reserved username check failed'

    # Register new test user
    test_user = 'testcreator'
    User.objects.filter(username=test_user).delete()
    res = client.post('/auth/register/', {
        'username': test_user,
        'display_name': 'Test Creator',
        'email': 'testcreator@example.com',
        'password1': 'SecretBio987!#',
        'password2': 'SecretBio987!#',
    })
    assert res.status_code == 302, f'Register failed: {res.status_code}'
    user = User.objects.get(username=test_user)
    profile = user.profile
    assert profile.display_name == 'Test Creator'
    print('  [PASS] Registration & Profile creation signal')

    # Login
    client.login(username=test_user, password='SecretBio987!#')
    res = client.get('/dashboard/')
    assert res.status_code == 200, f'Dashboard overview failed: {res.status_code}'
    print('  [PASS] Dashboard overview')

    print('=== 2. TEST LINK MANAGEMENT & REORDERING ===')
    # Add links
    res = client.post('/dashboard/links/', {
        'title': 'My YouTube Channel',
        'url': 'https://youtube.com/@testcreator',
        'description': 'Watch my videos',
        'icon': 'video',
        'is_active': 'on'
    })
    assert res.status_code == 302

    res = client.post('/dashboard/links/', {
        'title': 'My Store',
        'url': 'https://store.example.com',
        'description': 'Buy my merch',
        'icon': 'shopping-bag',
        'is_active': 'on'
    })
    assert res.status_code == 302

    links = list(profile.links.all().order_by('order'))
    assert len(links) == 2, f'Expected 2 links, got {len(links)}'
    link1, link2 = links[0], links[1]
    print(f'  [PASS] Created 2 links: {link1.title} (order={link1.order}), {link2.title} (order={link2.order})')

    # Move link2 up
    res = client.post(f'/dashboard/links/{link2.id}/up/')
    assert res.status_code == 302
    links_after = list(profile.links.all().order_by('order'))
    assert links_after[0].id == link2.id, 'Move up failed'
    print('  [PASS] 1-click move_link_up succeeded')

    # Move link2 down
    res = client.post(f'/dashboard/links/{link2.id}/down/')
    assert res.status_code == 302
    links_after2 = list(profile.links.all().order_by('order'))
    assert links_after2[0].id == link1.id, 'Move down failed'
    print('  [PASS] 1-click move_link_down succeeded')

    # Reorder API
    reorder_payload = json.dumps({'order': [link2.id, link1.id]})
    res = client.post('/dashboard/links/api/reorder/', 
        data=reorder_payload,
        content_type='application/json'
    )
    assert res.status_code == 200, f'Reorder API failed: {res.status_code}'
    links_reordered = list(profile.links.all().order_by('order'))
    assert links_reordered[0].id == link2.id and links_reordered[1].id == link1.id, 'API reorder order mismatch'
    print('  [PASS] REST API reorder links succeeded')

    # Toggle link
    res = client.post(f'/dashboard/links/{link1.id}/toggle/')
    assert res.status_code == 302
    link1.refresh_from_db()
    assert not link1.is_active, 'Link toggle failed'
    # Toggle back to active
    client.post(f'/dashboard/links/{link1.id}/toggle/')
    link1.refresh_from_db()
    assert link1.is_active
    print('  [PASS] Toggle link active/inactive succeeded')

    print('=== 3. TEST SOCIAL MEDIA ===')
    res = client.post('/dashboard/social/', {
        'platform': 'github',
        'url': 'https://github.com/testcreator',
        'is_active': 'on'
    })
    assert res.status_code == 302
    assert profile.social_accounts.filter(platform='github').exists()
    print('  [PASS] Social account added')

    print('=== 4. TEST APPEARANCE SETTINGS ===')
    res = client.post('/dashboard/appearance/', {
        'theme': 'sunset_gradient',
        'bg_type': 'gradient',
        'bg_color': '#1e1b4b',
        'bg_gradient': 'linear-gradient(135deg, #1e1b4b 0%, #701a75 100%)',
        'text_color': '#ffffff',
        'button_style': 'glass',
        'button_shape': 'pill',
        'button_color': '#3b82f6',
        'button_text_color': '#ffffff',
        'font_family': 'inter',
        'avatar_shape': 'rounded',
        'profile_alignment': 'center'
    })
    assert res.status_code == 302
    profile.appearance.refresh_from_db()
    assert profile.appearance.theme == 'sunset_gradient'
    assert profile.appearance.button_shape == 'pill'
    print('  [PASS] Appearance updated to sunset_gradient / pill')

    print('=== 5. TEST PUBLIC PAGE & CLICKS ===')
    anon_client = Client()
    res = anon_client.get(f'/{test_user}/')
    assert res.status_code == 200, f'Public profile failed: {res.status_code}'
    content_str = res.content.decode()
    assert 'Test Creator' in content_str
    assert 'theme-sunset_gradient' in content_str
    print('  [PASS] Public creator profile rendered with correct theme')

    # Test link click redirection & click increment
    initial_clicks = link1.click_count
    res = anon_client.get(f'/l/{link1.id}/')
    assert res.status_code == 302
    assert res.url == link1.url
    link1.refresh_from_db()
    assert link1.click_count == initial_clicks + 1
    print('  [PASS] Click tracking redirect and atomic counter increment')

    # Test vCard download
    res = anon_client.get(f'/{test_user}/contact.vcf')
    assert res.status_code == 200
    assert res['Content-Type'].startswith('text/vcard')
    vcard_text = res.content.decode()
    assert 'BEGIN:VCARD' in vcard_text and 'Test Creator' in vcard_text
    print('  [PASS] vCard 3.0 export (.vcf) verified')

    print('=== 6. TEST BOOKING SYSTEM & DOUBLE BOOKING PREVENTION ===')
    # Add a service
    res = client.post('/dashboard/bookings/services/add/', {
        'title': 'Strategy Session',
        'description': '1-on-1 growth consulting',
        'duration_minutes': 30,
        'price': 75.00,
        'currency': 'USD',
        'instructions': 'Meeting link will be emailed to you.',
        'is_active': 'on'
    })
    assert res.status_code == 302
    service = profile.services.get(title='Strategy Session')
    print('  [PASS] Service created:', service.title)

    # Setup availability
    res = client.post('/dashboard/bookings/availability/', {
        'start_0': '09:00', 'end_0': '17:00', 'active_0': 'on',
        'start_1': '09:00', 'end_1': '17:00', 'active_1': 'on',
        'start_2': '09:00', 'end_2': '17:00', 'active_2': 'on',
        'start_3': '09:00', 'end_3': '17:00', 'active_3': 'on',
        'start_4': '09:00', 'end_4': '17:00', 'active_4': 'on',
        'start_5': '09:00', 'end_5': '17:00',
        'start_6': '09:00', 'end_6': '17:00',
    })
    assert res.status_code == 302
    print('  [PASS] Availability rules configured')

    # Find next upcoming weekday
    target_date = date.today() + timedelta(days=2)
    while target_date.weekday() >= 5:
        target_date += timedelta(days=1)
    date_str = target_date.strftime('%Y-%m-%d')

    # Get available slots via API
    res = anon_client.get(f'/{test_user}/api/slots/?service_id={service.id}&date={date_str}')
    assert res.status_code == 200
    data = res.json()
    slots = data.get('slots', [])
    assert len(slots) > 0, f'No slots found for {date_str}'
    chosen_slot = slots[0]
    print(f'  [PASS] Retrieved {len(slots)} available slots on {date_str}, selecting {chosen_slot}')

    # Book the chosen slot
    res = anon_client.post(f'/{test_user}/book/{service.id}/', {
        'booking_date': date_str,
        'booking_time': chosen_slot,
        'visitor_name': 'Jane Doe',
        'visitor_email': 'jane@example.com',
        'visitor_phone': '+1 555 432 1098',
        'notes': 'Looking forward to our call!'
    })
    assert res.status_code == 302
    booking = Booking.objects.get(profile=profile, visitor_email='jane@example.com')
    assert booking.status == 'pending'
    print('  [PASS] Booking request created successfully')

    # Check slot is now blocked
    res = anon_client.get(f'/{test_user}/api/slots/?service_id={service.id}&date={date_str}')
    slots_after = res.json().get('slots', [])
    assert chosen_slot not in slots_after, f'Slot {chosen_slot} was not blocked after booking!'
    print('  [PASS] Double-booking prevention: Slot is excluded from available slots')

    # Try duplicate booking directly
    res = anon_client.post(f'/{test_user}/book/{service.id}/', {
        'booking_date': date_str,
        'booking_time': chosen_slot,
        'visitor_name': 'Impostor',
        'visitor_email': 'impostor@example.com',
        'visitor_phone': '',
        'notes': 'Trying to steal slot'
    })
    assert Booking.objects.filter(profile=profile, visitor_email='impostor@example.com').count() == 0
    print('  [PASS] Duplicate booking was blocked with validation error')

    # Creator approves booking
    res = client.post(f'/dashboard/bookings/{booking.id}/status/', {'status': 'confirmed'})
    assert res.status_code == 302
    booking.refresh_from_db()
    assert booking.status == 'confirmed'
    print('  [PASS] Creator approved booking')

    print('=== 7. TEST CONTACT INQUIRIES & CSV EXPORT ===')
    res = anon_client.post(f'/{test_user}/contact/', {
        'name': 'Alex Partner',
        'email': 'alex@brand.com',
        'phone': '+1 555 987 6543',
        'message': 'Sponsorship collaboration opportunity.'
    })
    assert res.status_code == 302
    contact = ContactSubmission.objects.get(profile=profile, email='alex@brand.com')
    assert contact.name == 'Alex Partner'
    print('  [PASS] Contact inquiry submitted')

    # Creator exports contacts CSV
    res = client.get('/dashboard/contacts/export/')
    assert res.status_code == 200
    assert res['Content-Type'] == 'text/csv'
    assert 'Alex Partner' in res.content.decode()
    print('  [PASS] Contacts CSV export verified')

    print('=== 8. TEST DJANGO ADMIN ===')
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin_tester', 'adm@example.com', 'AdminPass123!')

    admin_client = Client()
    admin_client.force_login(admin_user)
    res = admin_client.get('/admin/')
    assert res.status_code == 200
    assert 'Django administration' in res.content.decode()
    print('  [PASS] Standard Django admin is active and accessible')

    # Cleanup test user
    User.objects.filter(username=test_user).delete()
    print('  [PASS] Test user cleaned up')

    print('\n>>> ALL 8 E2E WORKFLOW TESTS PASSED CLEANLY! <<<')

if __name__ == '__main__':
    run()
