from datetime import time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from apps.profiles.models import Profile, Appearance
from apps.links.models import Link
from apps.social.models import SocialAccount
from apps.bookings.models import Service, AvailabilityRule, Booking
from apps.contacts.models import ContactSubmission

class Command(BaseCommand):
    help = 'Seeds realistic creator demo data and administrator user'

    def handle(self, *args, **options):
        self.stdout.write("Seeding creator platform data in MariaDB...")

        # 1. Superuser
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@linkstudio.bio',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if admin_created:
            admin_user.set_password('AdminPass123!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' with password 'AdminPass123!'"))

        # 2. Eddie Scott creator user
        eddie_user, eddie_created = User.objects.get_or_create(
            username='eddiescott',
            defaults={
                'email': 'eddie@eddiescott.dev',
                'first_name': 'Eddie',
                'last_name': 'Scott',
            }
        )
        if eddie_created:
            eddie_user.set_password('CreatorPass123!')
            eddie_user.save()
            self.stdout.write(self.style.SUCCESS("Created creator 'eddiescott' with password 'CreatorPass123!'"))

        profile = eddie_user.profile
        profile.display_name = 'Eddie Scott'
        profile.bio = "Creator, Consultant & Speaker. Helping modern founders scale indie products from GH₵0 to GH₵100k ARR."
        profile.location = "Accra, Ghana"
        profile.website = "https://eddiescott.dev"
        profile.public_email = "hello@eddiescott.dev"
        profile.phone = "+233 24 888 2345"
        profile.show_contact_form = True
        profile.show_save_contact = True
        profile.is_public = True
        profile.total_views = 342
        profile.save()

        # Appearance configuration
        appearance = profile.appearance
        appearance.theme = 'midnight_dark'
        appearance.button_style = 'glass'
        appearance.button_shape = 'rounded'
        appearance.button_color = '#3b82f6'
        appearance.button_text_color = '#ffffff'
        appearance.font_family = 'inter'
        appearance.avatar_shape = 'circle'
        appearance.profile_alignment = 'center'
        appearance.save()

        # 3. Links
        Link.objects.filter(profile=profile).delete()
        links_data = [
            {'title': '🚀 Join My Free Creator Community', 'url': 'https://discord.com', 'icon': 'sparkles', 'description': '5,000+ indie builders and creators collaborating daily', 'order': 0, 'click_count': 124},
            {'title': '📹 Watch My Latest Founder Breakdown', 'url': 'https://youtube.com', 'icon': 'video', 'description': 'How we scaled to $50k MRR without venture capital', 'order': 1, 'click_count': 89},
            {'title': '📑 Download The SaaS Launch Checklist', 'url': 'https://gumroad.com', 'icon': 'file-text', 'description': 'A 42-point interactive checklist for your next big product release', 'order': 2, 'click_count': 64},
            {'title': '🎙️ Listen to The Studio Podcast', 'url': 'https://spotify.com', 'icon': 'podcast', 'description': 'Deep dives into engineering, marketing, and creator monetization', 'order': 3, 'click_count': 41},
            {'title': '⭐ Support Open Source on GitHub', 'url': 'https://github.com', 'icon': 'star', 'description': 'Explore my libraries, boilerplate templates, and tools', 'order': 4, 'click_count': 32},
        ]
        for item in links_data:
            Link.objects.create(profile=profile, **item)
        self.stdout.write(self.style.SUCCESS(f"Created {len(links_data)} creator links."))

        # 4. Social Accounts
        SocialAccount.objects.filter(profile=profile).delete()
        socials_data = [
            {'platform': 'youtube', 'url': 'https://youtube.com/@eddiescott', 'order': 0},
            {'platform': 'twitter', 'url': 'https://x.com/eddiescott', 'order': 1},
            {'platform': 'github', 'url': 'https://github.com/eddiescott', 'order': 2},
            {'platform': 'linkedin', 'url': 'https://linkedin.com/in/eddiescott', 'order': 3},
            {'platform': 'spotify', 'url': 'https://spotify.com', 'order': 4},
            {'platform': 'instagram', 'url': 'https://instagram.com/eddiescott', 'order': 5},
        ]
        for item in socials_data:
            SocialAccount.objects.create(profile=profile, **item)
        self.stdout.write(self.style.SUCCESS(f"Created {len(socials_data)} social accounts."))

        # 5. Services & Availability
        Service.objects.filter(profile=profile).delete()
        service1 = Service.objects.create(
            profile=profile,
            title='1-on-1 Founder Consultation',
            description='Deep dive into your product roadmap, marketing funnel, or link-in-bio monetization strategies.',
            duration_minutes=30,
            price=75.00,
            instructions='You will receive a Google Meet link and calendar invitation immediately after approval.',
            order=0
        )
        service2 = Service.objects.create(
            profile=profile,
            title='Full Codebase & Architecture Review',
            description='In-depth architectural review of your Django, API, or database architecture with actionable feedback.',
            duration_minutes=60,
            price=180.00,
            instructions='Please provide your repository access or documentation in advance.',
            order=1
        )
        service3 = Service.objects.create(
            profile=profile,
            title='Quick Q&A Strategy Session',
            description='15-minute focused discussion on a specific technical or growth hurdle.',
            duration_minutes=15,
            price=40.00,
            instructions='Prepare 2-3 specific questions so we can hit the ground running.',
            order=2
        )
        self.stdout.write(self.style.SUCCESS("Created 3 booking services."))

        # Availability Rules (Mon-Fri 09:00 - 17:00)
        AvailabilityRule.objects.filter(profile=profile).delete()
        for day in range(5):
            AvailabilityRule.objects.create(
                profile=profile,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_active=True
            )
        self.stdout.write(self.style.SUCCESS("Configured Mon-Fri availability schedule."))

        # 6. Sample Bookings
        Booking.objects.filter(profile=profile).delete()
        now = timezone.now()
        tomorrow_10am = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        day_after_2pm = (now + timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)

        Booking.objects.create(
            profile=profile,
            service=service1,
            visitor_name='Sarah Jenkins',
            visitor_email='sarah.j@startupco.io',
            visitor_phone='+233 24 234 5678',
            notes='We need advice on shifting from freemium to premium tiers.',
            start_time=tomorrow_10am,
            end_time=tomorrow_10am + timedelta(minutes=30),
            status='confirmed',
            payment_status='paid'
        )

        Booking.objects.create(
            profile=profile,
            service=service2,
            visitor_name='Marcus Vance',
            visitor_email='marcus@cloudstack.com',
            notes='Review our multi-tenant database migration and indexing strategy.',
            start_time=day_after_2pm,
            end_time=day_after_2pm + timedelta(minutes=60),
            status='pending',
            payment_status='unpaid'
        )
        self.stdout.write(self.style.SUCCESS("Created sample incoming bookings."))

        # 7. Contact Submissions
        ContactSubmission.objects.filter(profile=profile).delete()
        ContactSubmission.objects.create(
            profile=profile,
            name='Liam Chen',
            email='liam@venturepartners.com',
            phone='+233 24 777 9999',
            message='Hi Eddie, saw your latest podcast on creator monetization. Would love to invite you as a keynote speaker for our Creator Summit next month!'
        )
        ContactSubmission.objects.create(
            profile=profile,
            name='Elena Rostova',
            email='elena@designstudio.de',
            message='Great work on the open source boilerplates! Are you open to co-hosting a YouTube livestream on UI design systems?'
        )
        self.stdout.write(self.style.SUCCESS("Created sample contact leads."))

        self.stdout.write(self.style.SUCCESS("\nDone! Demo platform seeded successfully."))
        self.stdout.write(self.style.SUCCESS("Creator page URL: http://127.0.0.1:8000/eddiescott/"))
        self.stdout.write(self.style.SUCCESS("Creator login: eddiescott / CreatorPass123!"))
        self.stdout.write(self.style.SUCCESS("Admin login: admin / AdminPass123!"))
