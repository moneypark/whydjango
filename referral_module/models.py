import logging

from decimal import Decimal

from django.db.models import F
from random import choice

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models, transaction
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.http import HttpRequest
from registration.signals import user_registered

from referral_module.utils import ChoiceEnum
from . import constants

logger = logging.getLogger('bootcamp.{}'.format(__file__))


class CreatedDateModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


def default_bonus_policy():
    return {
        'click': 0,
        'registration': 0,
    }


class Campaign(CreatedDateModel):
    key = models.CharField(
        verbose_name='Campaign key',
        max_length=7,
        unique=True
    )
    description = models.TextField(
        blank=True, null=True
    )
    is_active = models.BooleanField(
        default=True
    )
    bonus_policy = JSONField(
        default=default_bonus_policy
    )
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    def __str__(self):
        return self.key


class UserReferrer(CreatedDateModel):
    user = models.ForeignKey('auth.User')
    campaign = models.ForeignKey(Campaign, related_name='user_referrers')
    key = models.CharField(
        verbose_name='Unique referrer key',
        max_length=7,
        unique=True
    )
    reward = models.DecimalField(
        max_digits=10, decimal_places=3,
        default=0
    )

    class Meta:
        verbose_name = 'User referrer'
        verbose_name_plural = 'User referrers'
        unique_together = ('user', 'campaign', )

    def save(self, *args, **kwargs):
        attempts = 5

        if not self.key:
            while not self.key and attempts:
                self.key = "".join(
                    [choice(constants.KEY_ALPHABET) for i in range(7)]
                )
                with transaction.atomic():
                    try:
                        super(UserReferrer, self).save(*args, **kwargs)
                    except IntegrityError as e:
                        attempts -= 1
        else:
            super(UserReferrer, self).save(*args, **kwargs)

    def __str__(self):
        return 'Campaign: {} {} -key-> {}'.format(
            self.campaign.key, self.user.username, self.key
        )


class StatsType(ChoiceEnum):
    click = 'click'


class UserReferrerStats(CreatedDateModel):
    user_referrer = models.ForeignKey(UserReferrer, verbose_name='stats')
    event_type = models.CharField(
        choices=StatsType.choices(), default=StatsType.click,
        max_length=50, db_index=True
    )
    ip = models.GenericIPAddressField()
    context = JSONField(
        blank=True, null=True
    )

    class Meta:
        verbose_name = 'User referrer stats'
        verbose_name_plural = 'User referrer stats'

    def __str__(self):
        return "{} event at {}".format(
            self.event_type, self.created
        )


class Referrer(CreatedDateModel):
    registered_user = models.ForeignKey('auth.User')
    user_referrer = models.ForeignKey(UserReferrer)

    def __str__(self):
        return self.registered_user.username

    class Meta:
        verbose_name = 'Referrer'
        verbose_name_plural = 'Referrers'


@receiver(user_registered)
def associate_registered_user_with_referral(sender,  **kwargs):
    request = kwargs.get('request')  # type: HttpRequest
    user = kwargs.get('user')  # type: User

    referral_cookies_data = request.COOKIES.get(constants.REFERRER_COOKIE_NAME)  # type: str
    if referral_cookies_data:
        campaign_key, user_referrer_key = referral_cookies_data.split(':')
        campaign = Campaign.objects.filter(
            key=campaign_key

        ).first()
        user_referrer = UserReferrer.objects.filter(
            campaign=campaign,
            key=user_referrer_key
        ).first()
        if user_referrer:
            referrer, created = Referrer.objects.get_or_create(
                registered_user=user,
                user_referrer=user_referrer
            )

            # update user's reward
            user_referrer.reward = F('reward') + Decimal(user_referrer.campaign.bonus_policy['registration'])
            user_referrer.save(update_fields=['reward', ])
            logger.debug(
                'New referrer %s', referrer
            )
