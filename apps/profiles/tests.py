from django.test import TestCase
from django.contrib.auth.models import User
from apps.profiles.models import Profile, Appearance
from apps.contacts.vcard import generate_vcard_content

class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='eddiescott',
            email='eddie@example.com',
            password='Password123!',
            first_name='Eddie',
            last_name='Scott'
        )

    def test_signals_created_profile_and_appearance(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.username, 'eddiescott')
        self.assertTrue(hasattr(self.user.profile, 'appearance'))
        self.assertEqual(self.user.profile.appearance.theme, 'midnight_dark')

    def test_public_profile_view_success(self):
        response = self.client.get('/eddiescott/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eddie Scott')
        self.assertContains(response, '@eddiescott')

    def test_public_profile_nonexistent_returns_404(self):
        response = self.client.get('/nonexistentuser999/')
        self.assertEqual(response.status_code, 404)

    def test_vcard_generation(self):
        profile = self.user.profile
        profile.public_email = 'hello@eddiescott.com'
        profile.phone = '+1 555 999 8888'
        profile.save()

        vcard_text = generate_vcard_content(profile)
        self.assertIn('BEGIN:VCARD', vcard_text)
        self.assertIn('FN:Eddie Scott', vcard_text)
        self.assertIn('EMAIL;TYPE=INTERNET,PREF:hello@eddiescott.com', vcard_text)
        self.assertIn('TEL;TYPE=CELL,VOICE:+1 555 999 8888', vcard_text)
        self.assertIn('END:VCARD', vcard_text)

    def test_vcard_download_endpoint(self):
        response = self.client.get('/eddiescott/contact.vcf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/vcard; charset=utf-8')
        self.assertIn('attachment; filename="eddiescott.vcf"', response['Content-Disposition'])

    def test_vcard_escaping_special_characters(self):
        profile = self.user.profile
        profile.display_name = 'Doe, Jr.; John'
        profile.bio = 'Line 1\r\nLine 2; with, semicolons & commas\\backslashes'
        profile.save()

        vcard_text = generate_vcard_content(profile)
        self.assertIn(r'FN:Doe\, Jr.\; John', vcard_text)
        self.assertIn(r'N:Jr.\; John;Doe\,;;;', vcard_text)
        self.assertIn(r'NOTE:Line 1 Line 2\; with\, semicolons & commas\\backslashes', vcard_text)
        self.assertTrue(vcard_text.startswith("BEGIN:VCARD\r\n"))
        self.assertTrue(vcard_text.endswith("END:VCARD\r\n"))

