from django.test import TestCase
from django.urls import reverse
from referral_module.tests import factories
from referral_module import models


class CampaignsApiTestCase(TestCase):
    def setUp(self):
        self.user = factories.UserFactory(
            username='usertest',
        )
        self.client.force_login(self.user)
        self.campaigns = []
        for i in range(0, 5):
            self.campaigns.append(factories.CampaignFactory(
                description='some some'
            ))
        self.campaign = self.campaigns[0]

    def test_campaigns_list_api(self):
        url = reverse(
            'api-campaigns-list'
        )
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # Check that the rendered context contains 5 customers.
        self.assertEqual(data['count'], 5)

    def test_campaigns_details_api(self):
        pk = self.campaign.id
        url = reverse(
            'api-campaign-detail', args=(pk,)
        )
        response = self.client.get(url)
        data = response.json()

        # Check get all 9 fields
        self.assertEqual(len(data), 3)

        # Check get the right campaign details
        self.assertEqual(data['id'], self.campaign.id)

    def test_illegal_user_campaigns_details_api(self):
        fake_campaign_id = 1
        url = reverse(
            'api-campaign-detail', args=(fake_campaign_id,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        pk = self.campaign.id
        url = reverse(
            'api-campaign-detail', args=(pk,)
        )
        self.client.logout()
        response = self.client.get(url)

        # Check data not provides to unauthenticated users
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_referral_key_api(self):
        pk = self.campaign.id
        url = reverse(
            'api-referral-key', args=(pk, )
        )
        response = self.client.get(url)
        data = response.json()

        # Check that there is no user referrer
        self.assertEqual(data['user_referrer'], '')

        response = self.client.post(url)

        # Check that the response is 201 OK.
        self.assertEqual(response.status_code, 201)

        response = self.client.get(url)
        data = response.json()

        # Check user referrer is not empty
        self.assertNotEqual(data['user_referrer'], '')

        user_referrer_campaign = models.UserReferrer.objects.get(key=data['user_referrer'])

        # Check user_referrer_campaign key is correct
        self.assertEqual(user_referrer_campaign.campaign, self.campaign)

    def test_illegal_user_referral_key_api(self):
        self.client.logout()
        pk = self.campaign.id
        url = reverse(
            'api-referral-key', args=(pk,)
        )
        response = self.client.get(url)

        # Check data not provides to unauthenticated users
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
