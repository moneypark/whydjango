from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpRequest

from .factories import UserReferrerFactory, UserFactory

from referral_module import constants
from referral_module import models


def make_cookie_file(user_referrer):
    cookie_file = '{}:{}'.format(user_referrer.campaign.key, user_referrer.key)
    return cookie_file


def make_new_policy(click, registration):
    return{
        'click': click,
        'registration': registration,
    }


def get_request(user_referrer):
    request = HttpRequest()
    cookie = make_cookie_file(user_referrer)
    request.COOKIES[constants.REFERRER_COOKIE_NAME] = cookie
    return request


class UserRegisteredTestCase(TestCase):
    def test_user_registered_with_referrer_user(self):
        user = UserFactory()
        user_referrer = UserReferrerFactory()
        user_referrer.campaign.bonus_policy = make_new_policy(click=1, registration=6)
        user_referrer.campaign.save(update_fields=['bonus_policy', ])

        reward_before_new_user = user_referrer.reward
        request = get_request(user_referrer=user_referrer)
        models.associate_registered_user_with_referral("", user=user, request=request)

        # referrer user sign as referrer to the new user
        referrer_db = models.Referrer.objects.get(user_referrer=user_referrer)
        self.assertEqual(referrer_db.registered_user.username, user.username)

        # check reward update
        reward_of_referrer_user = models.UserReferrer.objects.get(key=user_referrer.key).reward
        reward_after_adding_user = reward_before_new_user + user_referrer.campaign.bonus_policy['registration']
        self.assertEqual(reward_of_referrer_user, reward_after_adding_user)

    def test_unreferred_user_registered(self):
        user = UserFactory()
        request = HttpRequest()
        models.associate_registered_user_with_referral("", user=user, request=request)

        # new user is in the database
        user_in_db = User.objects.get(username=user.username)
        self.assertEqual(user_in_db.username, user.username)

    def test_illegal_referrer_data(self):
        user = UserFactory()
        fake_user_referrer = UserReferrerFactory()
        fake_user_referrer.campaign.bonus_policy = make_new_policy(click=1, registration=6)
        fake_user_referrer.campaign.save(update_fields=['bonus_policy', ])

        real_user_campaign_key = fake_user_referrer.campaign.key
        # First check with fake campaign key
        fake_user_referrer.campaign.key = 77777  # random data
        request = get_request(user_referrer=fake_user_referrer)

        self.assertEqual(
            models.Referrer.objects.count(),
            0
        )
        models.associate_registered_user_with_referral("", user=user, request=request)

        self.assertEqual(
            models.Referrer.objects.count(),
            0
        )

        # check real campaign key and fake referrer
        fake_user_referrer.campaign.key = real_user_campaign_key
        fake_user_referrer.key = '232323'  # fake data

        request = get_request(user_referrer=fake_user_referrer)
        models.associate_registered_user_with_referral("", user=user, request=request)

        self.assertEqual(
            models.Referrer.objects.count(),
            0
        )
