from django.test import TestCase

from .factories import UserReferrerFactory


class UserReferrerModelTestCase(TestCase):
    def test_key_autogeneration(self):
        user_referrer = UserReferrerFactory()
        self.assertTrue(user_referrer.key)

        user_referrer.key = None
        user_referrer.save()
        self.assertTrue(user_referrer.key)
