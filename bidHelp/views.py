#coding=utf-8

from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
import bidHelp.models

def postlogin(request):
    return render(request,'bidHelp/login.html')

def login(request):
    id = request.GET.get('uID')
    PassWord = request.GET.get('uPassWord')
    userSet = bidHelp.models.User.objects.filter(uID=id)
    user = userSet[0]
    if(user.uPassword == PassWord):
        request.session['uID'] = user.uID
        return redirect(reverse('bidHelp:index'))
    else:
        return render(request,'bidHelp/login.html')

def index(request):
    uID = request.session.get('uID')
    userSet = bidHelp.models.User.objects.filter(uID=uID)
    user = userSet[0]
    return render(request, 'bidHelp/index.html', {'uKind': user.uKind})

