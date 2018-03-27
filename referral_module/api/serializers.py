from rest_framework import serializers
from referral_module import models
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', )


class UserReferrerSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.UserReferrer
        fields = ('user', 'key', )

    def get_user(self, obj):
        """
        get the user name
        :param obj:
        :return: username
        """
        return obj.user.username


class CampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Campaign
        fields = ('id', 'key', 'description', 'is_active', 'created',)


class CampaignDetailsSerializer(serializers.ModelSerializer):

    user_referrers = UserReferrerSerializer(many=True)

    class Meta:
        model = models.Campaign
        fields = (
            'id', 'key', 'user_referrers',
        )


class CampaignUserReferralSerializer(serializers.ModelSerializer):

    user_referrer = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Campaign
        fields = (
            'user_referrer',
        )

    def get_user_referrer(self, obj):
        """
        get the user referrer key if exist, otherwise return ''
        :param obj:
        :return: user referrer key
        """
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            user = request.user
        else:
            raise Exception('Authentication required')
        campaign = obj
        if user and obj:
            user_referrers_qs = models.UserReferrer.objects.filter(
                user=user,
                campaign=campaign
            )
        else:
            return ''
        return user_referrers_qs.first().key if user_referrers_qs.exists() else ''

    def generate_user_referrer(self):
        """
        create user referrer from a given user and campaign
        :return: user_referrer
        """
        user_referrer, _ = models.UserReferrer.objects.get_or_create(
            user=self.context['request'].user,
            campaign=self.context['view'].get_object()
        )
        return user_referrer
