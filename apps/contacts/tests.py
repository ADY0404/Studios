from django.test import TestCase
from django.contrib.auth.models import User
from apps.contacts.models import ContactSubmission

class ContactTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='contactuser', email='cu@example.com', password='Password123!')
        self.profile = self.user.profile

    def test_contact_submission_via_public_page(self):
        from django.core import mail
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
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Dave Visitor', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['cu@example.com'])


    def test_export_contacts_csv_sanitizes_formula_injection(self):
        ContactSubmission.objects.create(
            profile=self.profile,
            name='=cmd|/c calc!A0',
            email='+test@example.com',
            phone='-1234567890',
            message='=cmd|/C calc.exe'
        )
        self.client.force_login(self.user)
        response = self.client.get('/dashboard/contacts/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn("'=cmd|/C calc.exe", content)
        self.assertIn("'=cmd|/c calc!A0", content)
        self.assertIn("'+test@example.com", content)
        self.assertIn("'-1234567890", content)

    def test_submit_contact_rate_limiting(self):
        from django.core.cache import cache
        cache.clear()

        # Submit 5 times (allowed)
        for i in range(5):
            res = self.client.post('/contactuser/contact/', {
                'name': f'Visitor {i}',
                'email': f'v{i}@example.com',
                'message': f'Message {i}'
            }, REMOTE_ADDR='198.51.100.42')
            self.assertEqual(res.status_code, 302)

        self.assertEqual(ContactSubmission.objects.filter(profile=self.profile).count(), 5)

        # 6th submission from the same IP should be throttled
        res_throttled = self.client.post('/contactuser/contact/', {
            'name': 'Visitor 6',
            'email': 'v6@example.com',
            'message': 'Message 6'
        }, REMOTE_ADDR='198.51.100.42', follow=True)

        self.assertEqual(res_throttled.status_code, 200)
        self.assertContains(res_throttled, "Too many messages sent from your network")
        # Ensure 6th submission was not stored in the database
        self.assertEqual(ContactSubmission.objects.filter(profile=self.profile).count(), 5)

    def test_contacts_pagination(self):
        ContactSubmission.objects.bulk_create([
            ContactSubmission(
                profile=self.profile,
                name=f'Bulk User {i}',
                email=f'bulk{i}@example.com',
                message='Testing pagination'
            )
            for i in range(28)
        ])
        self.client.force_login(self.user)

        resp1 = self.client.get('/dashboard/contacts/')
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(len(resp1.context['contacts']), 25)
        self.assertTrue(resp1.context['contacts'].has_next())

        resp2 = self.client.get('/dashboard/contacts/?page=2')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.context['contacts']), 3)
        self.assertFalse(resp2.context['contacts'].has_next())



