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




]