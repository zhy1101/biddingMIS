from django.urls import path
from django.conf.urls import include, url
import bidHelp.views as views

urlpatterns =[
    url(r'^$',views.index,name='index')


]