#coding=utf-8

from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
import bidHelp.models

def postlogin(request):
    return render(request,'bidHelp/login.html')

def login(request):
    uID = request.POST['uID']
    PassWord = request.POST['uPassWord']
    user = bidHelp.models.User.objects.filter(uID=uID)
    if(user.uPassword == PassWord):
        session = request.Session()
        UA = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36"
        headers = {"User-Agent": UA,
                  "Referer": "http://www.v2ex.com/signin"}
        data = {
            "uID" : uID,
            "uKind" : user.uKind
        }
        response = session.post(url='bidHelp/index.html', headers=headers, data=data)
        return render(request,'bidHelp/index.html')
    else:
        return render(request,'bidHelp/login.html')

