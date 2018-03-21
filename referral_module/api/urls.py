from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^campaigns/$',
        views.CampaignList.as_view(),
        name='api-campaigns-list'),
    url(r'^campaigns/(?P<pk>[0-9]+)/$', views.CampaignDetail.as_view(),
        name='api-campaign-detail'),
    url(r'^campaigns/(?P<pk>[0-9]+)/referral_key/$', views.CampaignReferralNumber.as_view(),
        name='api-referral-key'),
    url(r'^users/$', views.UserList.as_view(),
        name='api-users-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(),
        name='api-user-details'),
    url(r'^api-auth/', include('rest_framework.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
