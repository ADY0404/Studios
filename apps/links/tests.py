import json
from django.test import TestCase
from django.contrib.auth.models import User
from apps.links.models import Link

class LinkTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='linktester', email='links@example.com', password='Password123!')
        self.profile = self.user.profile
        self.link1 = Link.objects.create(profile=self.profile, title='Link 1', url='https://example.com/1', order=0)
        self.link2 = Link.objects.create(profile=self.profile, title='Link 2', url='https://example.com/2', order=1)
        self.link3 = Link.objects.create(profile=self.profile, title='Link 3', url='https://example.com/3', order=2)

    def test_link_redirect_increments_click_count(self):
        initial_clicks = self.link1.click_count
        response = self.client.get(f'/l/{self.link1.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://example.com/1')
        
        self.link1.refresh_from_db()
        self.assertEqual(self.link1.click_count, initial_clicks + 1)

    def test_reorder_links_api(self):
        self.client.login(username='linktester', password='Password123!')
        # Reorder to [link3, link1, link2]
        payload = {'order': [self.link3.id, self.link1.id, self.link2.id]}
        response = self.client.post(
            '/dashboard/links/api/reorder/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'success')

        self.link3.refresh_from_db()
        self.link1.refresh_from_db()
        self.link2.refresh_from_db()
        
        self.assertEqual(self.link3.order, 0)
        self.assertEqual(self.link1.order, 1)
        self.assertEqual(self.link2.order, 2)
