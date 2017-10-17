from django.http import HttpResponseBadRequest

from . import constants


class ReferrerStoreMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):

        campaign_session_key = 'cp'
        user_referral_session_key = 'uk'

        campaign_key = request.GET.get(campaign_session_key, None)
        user_referral_key = request.GET.get(user_referral_session_key, None)

        response = self.get_response(request)  # type: HttpResponseBadRequest

        if campaign_key and user_referral_key:
            response.set_cookie(
                constants.REFERRER_COOKIE_NAME, '{}:{}'.format(
                    campaign_key, user_referral_key
                )
            )

        return response
