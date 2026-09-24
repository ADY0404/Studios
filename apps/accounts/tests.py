from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core import mail
from apps.accounts.validators import validate_username
from apps.profiles.models import Profile


class AccountTests(TestCase):
    def test_validate_username_valid(self):
        self.assertEqual(validate_username('eddiescott'), 'eddiescott')
        self.assertEqual(validate_username('john_doe'), 'john_doe')
        self.assertEqual(validate_username('creator-123'), 'creator-123')

    def test_validate_username_reserved(self):
        reserved_names = ['admin', 'dashboard', 'login', 'register', 'api', 'contacts', 'bookings']
        for name in reserved_names:
            with self.assertRaises(ValidationError):
                validate_username(name)

    def test_validate_username_invalid_characters(self):
        invalid_names = ['hello world', 'user@domain', '$$money', '-leadingdash', 'trailingdot.']
        for name in invalid_names:
            with self.assertRaises(ValidationError):
                validate_username(name)

    def test_user_registration_and_email_confirmation_flow(self):
        mail.outbox.clear()
        # 1. Register new user
        response = self.client.post('/auth/register/', {
            'username': 'creatorjane',
            'display_name': 'Jane Doe',
            'email': 'jane@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Check your email")

        user = User.objects.filter(username='creatorjane').first()
        self.assertIsNotNone(user)
        # Account must be inactive until email is confirmed
        self.assertFalse(user.is_active)
        self.assertFalse(user.profile.is_email_verified)
        self.assertEqual(user.profile.display_name, 'Jane Doe')

        # 2. Check verification email was sent to user's email
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Confirm your LinkStudio email", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['jane@example.com'])
        email_body = mail.outbox[0].body
        self.assertIn("/auth/confirm-email/", email_body)

        # 3. User CANNOT log in before confirming email
        login_res = self.client.post('/auth/login/', {
            'username': 'creatorjane',
            'password': 'StrongPass123!'
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertContains(login_res, "You cannot log in until you confirm your email")

        # Extract confirmation URL from email
        import re
        url_match = re.search(r'(/auth/confirm-email/[^ \n\r]+)', email_body)
        self.assertIsNotNone(url_match)
        confirm_path = url_match.group(1)

        # 4. Click confirmation link
        confirm_res = self.client.get(confirm_path)
        self.assertEqual(confirm_res.status_code, 302)
        self.assertRedirects(confirm_res, '/auth/login/')

        # User is now active and email verified
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.is_email_verified)

        # 5. User can now successfully log in (using either username or email)
        login_success = self.client.post('/auth/login/', {
            'username': 'jane@example.com',
            'password': 'StrongPass123!'
        })
        self.assertEqual(login_success.status_code, 302)
        self.assertRedirects(login_success, '/dashboard/')

    def test_admin_has_full_access_to_dashboard(self):
        admin = User.objects.create_superuser(
            username='siteadmin',
            email='admin@example.com',
            password='AdminPassword123!'
        )
        self.client.force_login(admin)

        # Admin must have access to creator dashboard routes
        dash_res = self.client.get('/dashboard/')
        self.assertEqual(dash_res.status_code, 200)
        self.assertContains(dash_res, "Admin Console")

        # Admin must have access to settings
        settings_res = self.client.get('/auth/settings/')
        self.assertEqual(settings_res.status_code, 200)

    def test_password_reset_sends_email_with_custom_template(self):
        mail.outbox.clear()
        user = User.objects.create_user(
            username='resetuser',
            email='reset@example.com',
            password='InitialPassword123!'
        )
        user.profile.is_email_verified = True
        user.profile.save()

        # Request password reset
        response = self.client.post('/auth/password-reset/', {
            'email': 'reset@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/password-reset/done/')

        # Ensure reset email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset your LinkStudio password", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['reset@example.com'])
        self.assertIn("/auth/reset/", mail.outbox[0].body)
