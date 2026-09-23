from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apps.accounts.validators import validate_username

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

    def test_user_registration_flow(self):
        response = self.client.post('/auth/register/', {
            'username': 'creatorjane',
            'display_name': 'Jane Doe',
            'email': 'jane@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        # Should redirect to dashboard overview
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username='creatorjane').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.profile.display_name, 'Jane Doe')
        self.assertEqual(user.profile.appearance.theme, 'midnight_dark')
