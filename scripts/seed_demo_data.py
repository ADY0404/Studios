import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.profiles.models import Profile, Appearance
from apps.links.models import Link
from apps.social.models import SocialAccount
from apps.bookings.models import Service, AvailabilityRule

def seed():
    print('Seeding demo data into MariaDB Cloud...')

    # 1. Superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@linkstudio.bio', 'AdminPass123!')
        print('Created admin superuser: admin / AdminPass123!')
    else:
        print('Admin user already exists.')

    # 2. Demo Creator: eddiescott
    user, created = User.objects.get_or_create(
        username='eddiescott',
        defaults={'email': 'eddie@eddiescott.com'}
    )
    if created or not user.has_usable_password():
        user.set_password('CreatorPass123!')
        user.save()
    print('Creator account: eddiescott / CreatorPass123!')

    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            'username': 'eddiescott',
            'display_name': 'Eddie Scott',
            'bio': 'Creator, Consultant & Speaker.\nHelping founders and builders scale modern products.',
            'location': 'Accra, Ghana',
            'website': 'https://eddiescott.com',
            'public_email': 'hello@eddiescott.com',
            'phone': '+233 24 234 5678',
            'show_contact_form': True,
            'show_save_contact': True,
            'is_public': True
        }
    )
    profile.display_name = 'Eddie Scott'
    profile.bio = 'Creator, Consultant & Speaker.\nHelping founders and builders scale modern products.'
    profile.location = 'Accra, Ghana'
    profile.website = 'https://eddiescott.com'
    profile.public_email = 'hello@eddiescott.com'
    profile.phone = '+233 24 234 5678'
    profile.show_contact_form = True
    profile.show_save_contact = True
    profile.is_public = True
    profile.save()

    appearance, _ = Appearance.objects.get_or_create(
        profile=profile,
        defaults={
            'theme': 'midnight_dark',
            'button_style': 'glass',
            'button_shape': 'rounded',
            'font_family': 'inter',
            'avatar_shape': 'circle',
            'profile_alignment': 'center'
        }
    )

    # 3. Links
    sample_links = [
        ('My Official Website', 'https://eddiescott.com', 'Read essays, case studies, and latest announcements', 'globe', 1),
        ('Watch Latest Keynote', 'https://youtube.com', 'How to bootstrap high-growth creator businesses', 'video', 2),
        ('Read The Weekly Dispatch', 'https://substack.com', 'Actionable insights every Sunday morning', 'book-open', 3),
        ('Creator Growth Playbook', 'https://gumroad.com', 'Comprehensive 80-page guide with Notion templates', 'shopping-bag', 4),
        ('Open Source GitHub Repos', 'https://github.com', 'Boilerplates, developer tools, and micro-SaaS kits', 'code', 5),
    ]

    for title, url, desc, icon, order in sample_links:
        Link.objects.update_or_create(
            profile=profile,
            title=title,
            defaults={
                'url': url,
                'description': desc,
                'icon': icon,
                'order': order,
                'is_active': True
            }
        )
    print(f'Created {len(sample_links)} links.')

    # 4. Social Accounts
    sample_socials = [
        ('youtube', 'https://youtube.com/@eddiescott', 1),
        ('twitter', 'https://x.com/eddiescott', 2),
        ('linkedin', 'https://linkedin.com/in/eddiescott', 3),
        ('github', 'https://github.com/eddiescott', 4),
        ('spotify', 'https://open.spotify.com', 5),
    ]

    for platform, url, order in sample_socials:
        SocialAccount.objects.update_or_create(
            profile=profile,
            platform=platform,
            defaults={
                'url': url,
                'order': order,
                'is_active': True
            }
        )
    print(f'Created {len(sample_socials)} social accounts.')

    # 5. Bookable Services
    services_data = [
        ('1-on-1 Growth Consultation', 'Dedicated 30-minute advisory call covering strategy, audience building, and tech stack.', 30, 150.00, 'Meeting link provided via email.', 1),
        ('Comprehensive Product Audit', 'Deep dive 60-minute teardown of your creator platform, UX flows, and retention levers.', 60, 300.00, 'Please share your product link in notes.', 2),
    ]

    for title, desc, dur, price, instr, order in services_data:
        Service.objects.update_or_create(
            profile=profile,
            title=title,
            defaults={
                'description': desc,
                'duration_minutes': dur,
                'price': price,
                'currency': 'GHS',
                'instructions': instr,
                'order': order,
                'is_active': True
            }
        )
    print(f'Created {len(services_data)} bookable services.')

    # 6. Availability Rules (Mon-Fri 09:00 - 17:00)
    for day in range(5):
        AvailabilityRule.objects.update_or_create(
            profile=profile,
            day_of_week=day,
            defaults={
                'start_time': '09:00',
                'end_time': '17:00',
                'is_active': True
            }
        )
    print('Configured weekday availability rules.')
    print('Seeding completed successfully!')

if __name__ == '__main__':
    seed()

