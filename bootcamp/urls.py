from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from referral_module import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', views.CampaignListView.as_view(), name='campaign-list'),
    url(r'^campaign/(?P<pk>\d+)/$', views.CampaignDetailView.as_view(),
        name='campaign-detail'),
    url(r'^campaign/(?P<pk>\d+)/referral/new/$',
        views.CampaignNewReferralView.as_view(), name='campaign-new-referral'),
    url(r'^api/', include('referral_module.api.urls')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
