from django.test import TestCase
from django.urls import reverse


class CampaignListTestCase(TestCase):
    def setUp(self):
        self.url = reverse('campaign-list')

    def test_page_access(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertTemplateUsed(
            response,
            'campaign/list.html'
        )
