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









]