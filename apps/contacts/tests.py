from django.test import TestCase
from django.contrib.auth.models import User
from apps.contacts.models import ContactSubmission

class ContactTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='contactuser', email='cu@example.com', password='Password123!')
        self.profile = self.user.profile

    def test_contact_submission_via_public_page(self):
        response = self.client.post('/contactuser/contact/', {
            'name': 'Dave Visitor',
            'email': 'dave@external.org',
            'phone': '+1 555 444 3333',
            'message': 'Looking forward to collaborating with you!'
        })
        self.assertEqual(response.status_code, 302)
        
        submission = ContactSubmission.objects.filter(profile=self.profile, email='dave@external.org').first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.name, 'Dave Visitor')
        self.assertEqual(submission.message, 'Looking forward to collaborating with you!')
