from decimal import Decimal
from django.db.models.expressions import F
from django.http import HttpResponseBadRequest

from . import constants
from .models import (
    UserReferrerStats, UserReferrer
)


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
            self.update_referrer_data(request, user_referral_key)

        return response

    def update_referrer_data(self, request, user_referral_key):
        # store statistics
        meta = request.META
        try:
            user_referrer = UserReferrer.objects.get(
                key=user_referral_key
            )
            UserReferrerStats.objects.create(**{
                'user_referrer': user_referrer,
                'context': {
                    'HTTP_ACCEPT_LANGUAGE': meta.get('HTTP_ACCEPT_LANGUAGE'),
                    'HTTP_USER_AGENT': meta.get('HTTP_USER_AGENT'),
                },
                'ip': request.META['REMOTE_ADDR'],
            })

            # update user's reward
            user_referrer.reward = F('reward') + Decimal(user_referrer.campaign.bonus_policy['click'])
            user_referrer.save(update_fields=['reward', ])
        except UserReferrer.DoesNotExist:
            pass
