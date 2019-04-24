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
        request.session['uKind'] = user.uKind
        return redirect(reverse('bidHelp:index'))
    else:
        return render(request,'bidHelp/login.html')

def index(request):
    uID = request.session.get('uID')
    userSet = bidHelp.models.User.objects.filter(uID=uID)
    user = userSet[0]
    return render(request, 'bidHelp/index.html', {'uKind': user.uKind})

def showCustomerDistribution(request):
    return render(request, 'bidHelp/Preparation/CustomerList.html')

def toManageInvitation(request):
    invitationSet = bidHelp.models.BidInvitation.objects.filter(response__isnull=True)
    print(len(invitationSet))
    cdict = {}
    for invitation in invitationSet:
        customers = bidHelp.models.Customer.objects.filter(cID=invitation.cID.cID)
        cID = str(invitation.cID)
        cdict[cID] = customers[0].cName
    projectToCreate = bidHelp.models.Project.objects.filter(pState=23)
    print(len(projectToCreate))
    context = {'invitationSet':invitationSet,'cdict':cdict,'projectToCreate':projectToCreate}
    return render(request,'bidHelp/Preparation/invitationList.html',context)

def submitInvitation(request,Iid):
    obj = bidHelp.models.BidInvitation.objects.get(inviteID=int(Iid))
    obj.response = 'Y'
    obj.save()
    protentialProject = bidHelp.models.Project(inviteID=Iid,pState=23)
    protentialProject.save()
    return toManageInvitation

def refuseInvitation(request,Iid):
    obj = bidHelp.models.BidInvitation.objects.get(inviteID=int(Iid))
    obj.response = 'N'
    obj.save()
    return toManageInvitation


