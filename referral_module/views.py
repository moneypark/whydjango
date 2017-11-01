from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, View

from . import models


class CampaignListView(ListView):
    template_name = 'campaign/list.html'
    model = models.Campaign
    queryset = models.Campaign.objects.all()

    def get_queryset(self):
        qs = super(CampaignListView, self).get_queryset()
        qs = qs.extra(
            select={
                'user_referrer_key': (
                    "SELECT key FROM referral_module_userreferrer " +
                    "WHERE campaign_id=referral_module_campaign.id AND user_id=%s"
                )
            },
            select_params=(self.request.user.id, )
        )
        return qs


class CampaignDetailView(DetailView):
    template_name = 'campaign/detail.html'
    model = models.Campaign
    queryset = models.Campaign.objects.all().prefetch_related('user_referrers__user')

    def get_context_data(self, **kwargs):
        context = super(CampaignDetailView, self).get_context_data(**kwargs)
        context['user_referrers'] = self.get_object().user_referrers.all()
        return context


@method_decorator(login_required, name='dispatch')
class CampaignNewReferralView(View):
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        try:
            campaign = models.Campaign.objects.get(id=int(kwargs.get('pk')))
        except models.Campaign.DoesNotExist:
            campaign = None

        if campaign is None:
            response = HttpResponseBadRequest()
        else:
            user_referrer, _ = models.UserReferrer.objects.get_or_create(
                user=request.user,
                campaign=campaign
            )
            response = HttpResponseRedirect(reverse('campaign-detail', args=(campaign.id, )))
        return response
