from .serializers import CampaignSerializer, CampaignDetailsSerializer, CampaignUserReferralSerializer, UserSerializer
from rest_framework import generics, permissions
from referral_module import models
from django.contrib.auth.models import User


class UserList(generics.ListAPIView):
    """
    path: /api/users/
    get list of all the users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    """
    path: /api/users/<id>
    get user details
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CampaignList(generics.ListAPIView):
    """
    path: /api/campaigns/
    get list of all the campaigns
    """
    queryset = models.Campaign.objects.all()
    serializer_class = CampaignSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CampaignDetail(generics.RetrieveAPIView):
    """
    path: /api/campaigns/<id>
    get campaign details
    """
    queryset = models.Campaign.objects.all()
    serializer_class = CampaignDetailsSerializer

    permission_classes = (permissions.IsAuthenticated,)


class CampaignReferralNumber(
    generics.CreateAPIView,
    generics.RetrieveAPIView
):
    """
    path: /api/campaigns/<id>/referral_number
    get user referrer key or make one with post
    """
    queryset = models.Campaign.objects.filter(is_active=True)
    serializer_class = CampaignUserReferralSerializer

    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """
        triggered on post request - generate user referrer key
        :param serializer:
        """
        serializer.generate_user_referrer()
