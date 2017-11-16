from django.contrib.auth.models import User
import factory as factory_boy

from referral_module import models


class UserFactory(factory_boy.DjangoModelFactory):
    username = factory_boy.Sequence(lambda n: 'user-{}'.format(n))
    email = factory_boy.Sequence(lambda n: 'user-{}@moneypark.ch'.format(n))

    class Meta:
        model = User


class CampaignFactory(factory_boy.DjangoModelFactory):
    key = factory_boy.Sequence(lambda n: 'key-{}'.format(n))
    is_active = True

    class Meta:
        model = models.Campaign


class UserReferrerFactory(factory_boy.DjangoModelFactory):
    campaign = factory_boy.SubFactory(CampaignFactory)
    user = factory_boy.SubFactory(UserFactory)

    class Meta:
        model = models.UserReferrer
