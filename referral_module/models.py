from django.db import models


class CreatedDateModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


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
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    def __str__(self):
        return self.key


class UserReferrer(CreatedDateModel):
    user = models.ForeignKey('auth.User')
    campaign = models.ForeignKey(Campaign)
    key = models.CharField(
        verbose_name='Unique referrer key',
        max_length=7,
        unique=True
    )

    class Meta:
        verbose_name = 'User referrer'
        verbose_name_plural = 'User referrers'

    def __str__(self):
        return 'Campaign: {} {} -key-> {}'.format(
            self.campaign.key, self.user.username, self.key
        )


class Referrer(CreatedDateModel):
    registered_user = models.ForeignKey('auth.User')
    user_referrer = models.ForeignKey(UserReferrer)

    def __str__(self):
        return self.registered_user

    class Meta:
        verbose_name = 'Referrer'
        verbose_name_plural = 'Referrers'
