from django.urls import path
from django.conf.urls import include, url
import bidHelp.views as views

urlpatterns =[
    url(r'^$',views.postlogin, name='postlogin'),
    url(r'^login$',views.login, name='login'),
    url(r'^index$',views.index, name='index'),
    url(r'^toCustomerList$',views.showCustomerDistribution,name='showCustomerDistribution'),
    url(r'^toManageInvitation$',views.toManageInvitation,name='toManageInvitation'),
    url(r'^submitInvitation/(?P<Iid>\d*)$',views.submitInvitation,name='submitInvitation'),
    url(r'^refuseInvitation/(?P<Iid>\d*)$',views.refuseInvitation,name='refuseInvitation'),
    url(r'^adminProjectRequest/(?P<npIndex>[0-9]*)/(?P<rpIndex>[0-9]*)$',views.adminProjectRequest,name='adminProjectRequest'),
    url(r'^posttoAddProjectRequest/(?P<pID>[0-9]*)$',views.posttoAddProjectRequest,name='posttoAddProjectRequest'),
    url(r'^AddProjectRequest$', views.AddProjectRequest, name='AddProjectRequest'),
    url(r'^showProjectRequest/(?P<pID>[0-9]*)$', views.showProjectRequest, name='showProjectRequest'),
    url(r'^showBidRequestforST/(?P<uID>[0-9]*)$', views.showBidRequestforST, name='showBidRequestforST'),
    url(r'^tofastBidDocPage$', views.tofastBidDocPage, name='tofastBidDocPage'),
    url(r'^download_report/(?P<pID>[0-9]*)$', views.download_report, name='download_report'),
    url(r'^toBidPredictPage$', views.toBidPredictPage, name='toBidPredictPage'),
    url(r'^handleBidPricePredict$', views.handleBidPricePredict, name='handleBidPricePredict'),
    url(r'^adminBankGuarantee$', views.adminBankGuarantee, name='adminBankGuarantee'),
    url(r'^applyGuarantee/(?P<pID>[0-9]*)$', views.applyGuarantee, name='applyGuarantee'),
    url(r'^adminBidDocCheck$', views.adminBidDocCheck, name='adminBidDocCheck'),
    url(r'^applyBidCheck/(?P<pID>[0-9]*)/(?P<bidPrice>[0-9]*)$', views.applyBidCheck, name='applyBidCheck'),
    url(r'^finishBidCheck/(?P<pID>[0-9]*)$', views.finishBidCheck, name='finishBidCheck'),
    url(r'^adminBidNotice$', views.adminBidNotice, name='adminBidNotice'),
    url(r'^castBidNotice/(?P<pID>[0-9]*)/(?P<bidDate>.+)/(?P<bidPlace>.+)$', views.castBidNotice, name='castBidNotice'),
    url(r'^adminBidOpen$', views.adminBidOpen, name='adminBidOpen'),
    url(r'^reportResult_win/(?P<pID>[0-9]*)$', views.reportResult_win, name='reportResult_win'),
    url(r'^toLostReasonForm/(?P<pID>[0-9]*)$', views.toLostReasonForm, name='toLostReasonForm'),
    url(r'^reportResult_lost$', views.reportResult_lost, name='reportResult_lost'),
    url(r'^informWin/(?P<pID>[0-9]*)$', views.informWin, name='informWin'),
    url(r'^informLost/(?P<pID>[0-9]*)$', views.informLost, name='informLost'),
    url(r'^recentBidResult$', views.recentBidResult, name='recentBidResult'),
    url(r'^searchBidResultByWord/(?P<searchWord>.+)',views.searchBidResultByWord, name='searchBidResultByWord'),
    url(r'^adminExtralRequest', views.adminExtralRequest, name='adminExtralRequest'),
    url(r'^addURS_Page/(?P<pID>[0-9]*)$', views.addURS_Page, name='addURS_Page'),
    url(r'^addURS_handel$', views.addURS_handel, name='addURS_handel'),
    url(r'^answerURS_Page$', views.answerURS_Page, name='answerURS_Page'),
    url(r'^commitURS/(?P<URS_ID>[0-9]*)$', views.commitURS, name='commitURS'),
    url(r'^refuseURS/(?P<URS_ID>[0-9]*)/(?P<reason>.+)$', views.refuseURS, name='refuseURS'),
































]