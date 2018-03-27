from django.test import TestCase
from collections import OrderedDict
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from referral_module.tests import factories
from referral_module.api import serializers
from referral_module import models
from rest_framework.fields import DateTimeField


class SerializersApiTestCase(TestCase):
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

    def test_campaigns_list_serializer(self):
        queryset = models.Campaign.objects.all()
        serializer = serializers.CampaignSerializer(queryset, many=True)

        # Check that 5 campaigns was serialized
        self.assertEqual(len(serializer.data), 5)

        campaigns_data_list = []
        for campaign in self.campaigns:

            # to comply with djangorestframework datetime formatting
            date_time_object = DateTimeField()
            created = DateTimeField.to_representation(date_time_object, campaign.created)

            campaign_dict = OrderedDict(
                [
                    ('id', campaign.id), ('key', campaign.key), ('description', campaign.description),
                    ('is_active', campaign.is_active), ('created', created)
                ]
                                        )
            campaigns_data_list.append(campaign_dict)

        self.assertListEqual(serializer.data, campaigns_data_list)

        campaign_description = serializer.data[0]['description']

        # Check correct initial data
        self.assertEqual(campaign_description, "some some")

    def test_campaign_detail_serializer(self):
        factories.UserReferrerFactory(campaign=self.campaign, user=self.user)
        factory = APIRequestFactory()
        request = factory.get(reverse('api-referral-key', args=(self.campaign.id,)), content_type='application/json')
        request.user = self.user
        queryset = models.Campaign.objects.get(key=self.campaign.key)
        serializer = serializers.CampaignDetailsSerializer(queryset, context={'request': request})

        referrers_list = []
        referrers_data = self.campaign.user_referrers.all()
        for referrer in referrers_data:
            username = referrer.user
            referrer_key = referrer.key
            referrers_list.append(

                {
                    'user': username.username,
                    'key': referrer_key,
                }
            )
        campaign_data = {
            "id": self.campaign.id,
            'key': self.campaign.key,
            'user_referrers': referrers_list,
        }

        # Check correct initial data
        self.assertDictEqual(serializer.data, campaign_data)

    def test_campaign_user_referral_serializer(self):
        user_referrer = factories.UserReferrerFactory(campaign=self.campaign, user=self.user)
        pk = self.campaign.id
        factory = APIRequestFactory()
        request = factory.get(reverse('api-referral-key', args=(pk,)), content_type='application/json')
        request.user = self.user

        queryset = models.Campaign.objects.get(key=self.campaign.key)

        serializer = serializers.CampaignUserReferralSerializer(queryset, context={'request': request})
        serializer_user_referrer_key = serializer.get_user_referrer(self.campaign)

        # Check correct user referrer key
        self.assertEqual(user_referrer.key, serializer_user_referrer_key)

    def test_no_user_get_user_referrer(self):
        queryset = models.Campaign.objects.get(key=self.campaign.key)

        serializer = serializers.CampaignUserReferralSerializer(queryset)

        # Check get_user_method raise exception without user
        with self.assertRaisesMessage(Exception, 'Authentication required'):
            serializer.get_user_referrer(self.campaign)
