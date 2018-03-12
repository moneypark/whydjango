from django.test import TestCase
from django.http import HttpRequest
from django.http import HttpResponseBadRequest, HttpResponse
from referral_module import middleware, models, constants
from .factories import UserReferrerFactory, CampaignFactory


def request_response_helper(cp, uk, response_class=HttpResponse):
    """
        function that build response object - used to contain the cookies file
    :param cp:
    :param uk:
    :param response_class:
    :return: response object
    """
    request = HttpRequest()
    request.META['REMOTE_ADDR'] = '192.168.0.100'
    data_dict = {'cp': cp, 'uk': uk}
    request.GET = data_dict
    referrer_store = middleware.ReferrerStoreMiddleware(
        lambda request: response_class()
    )
    return referrer_store(request)


class MiddlewareTestCase(TestCase):
    def setUp(self):
        campaign = CampaignFactory(
            bonus_policy={
                'click': 6,
                'registration': 7,
            }
        )
        self.user_referrer = UserReferrerFactory(
            campaign=campaign
        )

        self.cp = self.user_referrer.campaign.key
        self.uk = self.user_referrer.key
        self.user_referrer_db = models.UserReferrer.objects.get(key=self.uk)

    def test_middleware_update_referrer_data(self):
        reward_before = self.user_referrer_db.reward
        response = request_response_helper(cp=self.cp, uk=self.uk, response_class=HttpResponse)

        # check response status code
        self.assertEqual(response.status_code, 200)

        self.user_referrer_db.refresh_from_db()
        reward_after = self.user_referrer_db.reward
        correct_reward = reward_before + self.user_referrer.campaign.bonus_policy['click']

        # check reward update correctly
        self.assertEqual(reward_after, correct_reward)

    def test_illegal_update_referrer_data(self):
        reward_before = self.user_referrer_db.reward
        response = request_response_helper(cp=self.cp, uk=self.uk, response_class=HttpResponseBadRequest)

        # check response status code
        self.assertEqual(response.status_code, 400)

        self.user_referrer_db.refresh_from_db()
        reward_after = self.user_referrer_db.reward
        correct_reward = reward_before + self.user_referrer.campaign.bonus_policy['click']

        # check reward was not update
        self.assertNotEqual(reward_after, correct_reward)

    def test_middleware_cookies_file(self):
        response = request_response_helper(cp=self.cp, uk=self.uk, response_class=HttpResponse)
        check_cookies = response.cookies[constants.REFERRER_COOKIE_NAME]
        check_cookies_value = check_cookies.value
        correct_cookies = "{}:{}".format(self.cp, self.uk)

        # check the cookies file
        self.assertEqual(check_cookies_value, correct_cookies)

    def test_missing_campaign_key(self):
        response = request_response_helper(cp="", uk=self.uk)

        self.assertNotIn(constants.REFERRER_COOKIE_NAME, response.cookies.keys())

    def test_missing_user_referrer_key(self):
        response = request_response_helper(cp=self.cp, uk="")

        self.assertNotIn(constants.REFERRER_COOKIE_NAME, response.cookies.keys())
