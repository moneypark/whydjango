from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpRequest

from .factories import UserReferrerFactory, UserFactory, CampaignFactory

from referral_module import constants
from referral_module import models


def make_cookie_file(user_referrer):
    cookie_file = '{}:{}'.format(user_referrer.campaign.key, user_referrer.key)
    return cookie_file


def get_request(user_referrer):
    request = HttpRequest()
    cookie = make_cookie_file(user_referrer)
    request.COOKIES[constants.REFERRER_COOKIE_NAME] = cookie
    return request


class UserRegisteredTestCase(TestCase):
    def setUp(self):
        campaign = CampaignFactory(
            bonus_policy={
                'click': 1,
                'registration': 6,
            }
        )
        self.user_referrer = UserReferrerFactory(
            campaign=campaign
        )
        self.user = UserFactory()

    def test_user_registered_with_referrer_user(self):
        reward_before_new_user = self.user_referrer.reward
        request = get_request(user_referrer=self.user_referrer)
        models.associate_registered_user_with_referral("", user=self.user, request=request)

        # referrer user sign as referrer to the new user
        referrer_db = models.Referrer.objects.get(user_referrer=self.user_referrer)
        self.assertEqual(referrer_db.registered_user.username, self.user.username)

        # check reward update
        reward_of_referrer_user = models.UserReferrer.objects.get(key=self.user_referrer.key).reward
        reward_after_adding_user = reward_before_new_user + self.user_referrer.campaign.bonus_policy['registration']
        self.assertEqual(reward_of_referrer_user, reward_after_adding_user)

    def test_unreferred_user_registered(self):
        request = HttpRequest()
        models.associate_registered_user_with_referral("", user=self.user, request=request)

        # new user is in the database
        user_in_db = User.objects.get(username=self.user.username)
        self.assertEqual(user_in_db.username, self.user.username)

    def test_illegal_referrer_data(self):

        real_user_campaign_key = self.user_referrer.campaign.key
        # First check with fake campaign key
        self.user_referrer.campaign.key = 77777  # random data
        request = get_request(user_referrer=self.user_referrer)

        self.assertEqual(
            models.Referrer.objects.count(),
            0
        )
        models.associate_registered_user_with_referral("", user=self.user, request=request)

        self.assertEqual(
            models.Referrer.objects.count(),
            0
        )

        # check real campaign key and fake referrer
        self.user_referrer.campaign.key = real_user_campaign_key
        self.user_referrer.key = '232323'  # fake data

        request = get_request(user_referrer=self.user_referrer)
        models.associate_registered_user_with_referral("", user=self.user, request=request)

        self.assertEqual(
            models.Referrer.objects.count(),
            0
        )
