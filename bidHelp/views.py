#coding=utf-8

from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
import bidHelp.models
from django.db.models import Q
from django.core.paginator import Paginator
import datetime

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
    invitationSet = bidHelp.models.BidInvitation.objects.exclude(Q(bidResponse='Y') | Q(bidResponse='N'))
    cdict = {}
    for invitation in invitationSet:
        customers = bidHelp.models.Customer.objects.filter(cID=invitation.cID.cID)
        cID = str(invitation.cID)
        cdict[cID] = customers[0].cName
    projectToCreate = bidHelp.models.Project.objects.filter(pState_id=23).distinct()
    context = {'invitationSet':invitationSet,'cdict':cdict,'projectToCreate':projectToCreate}
    return render(request,'bidHelp/Preparation/invitationList.html',context)

def submitInvitation(request,Iid):
    Iid = request.GET.get('Iid')
    obj = bidHelp.models.BidInvitation.objects.get(inviteID=Iid)
    obj.bidResponse = 'Y'
    obj.save()
    state = bidHelp.models.StateParam.objects.filter(paramID=23)
    protentialProject = bidHelp.models.Project(inviteID=obj,pState=state[0])
    protentialProject.save()
    return toManageInvitation(request)

def refuseInvitation(request,Iid):
    Iid = request.GET.get('Iid')
    obj = bidHelp.models.BidInvitation.objects.get(inviteID=Iid)
    obj.bidResponse = 'N'
    obj.save()
    return toManageInvitation(request)

def adminProjectRequest(request,npIndex,rpIndex):
    noListProject = bidHelp.models.Project.objects.filter(pState=23)
    np = Paginator(noListProject, 5)
    if npIndex == '':
        npIndex = '1'
    npIndex = int(npIndex)
    noListProject = np.page(npIndex)
    nplistrange = np.page_range
    readyProject = bidHelp.models.Project.objects.filter(pState_id__lt=21)
    rp = Paginator(readyProject, 5)
    if rpIndex == '':
        rpIndex = '1'
    rpIndex = int(rpIndex)
    readyProject = rp.page(rpIndex)
    rplistrange = rp.page_range
    context = {"noListProject":noListProject,"nplistrange":nplistrange,"npIndex":npIndex,
               "readyProject":readyProject,"rplistrange":rplistrange,"rpIndex":rpIndex}
    return render(request,'bidHelp/Preparation/adminProjectRequest.html',context)

def posttoAddProjectRequest(request,pID):
    project = bidHelp.models.Project.objects.get(pID = pID)
    deviceList = bidHelp.models.Device.objects.all()
    SSList  = bidHelp.models.User.objects.filter(uKind='SS')
    ST1List = bidHelp.models.User.objects.filter(uKind='TS')
    ST2List = bidHelp.models.User.objects.filter(uKind='BS')
    context = {"project":project,"deviceList":deviceList,"SSList":SSList,"ST1List":ST1List,"ST2List":ST2List}
    return  render(request,'bidHelp/Preparation/AddProjectRequest.html',context)

def AddProjectRequest(request):
    request.encoding = 'utf-8'
    #完善项目信息
    projectID = request.POST.get('pID')
    project = bidHelp.models.Project.objects.get(pID=projectID)
    project.pName = request.POST.get('pName')
    project.startTime = datetime.datetime.now().strftime('%Y-%m-%d')
    project.isGuaratee='N'
    device = bidHelp.models.Device.objects.get(id = request.POST.get('device_id'))
    project.aimDevice = device
    project.quantity = request.POST.get('quantity')
    state = bidHelp.models.StateParam.objects.get(paramID=1)
    project.pState = state
    project.save()
    #完善人员信息
    staff_st1 = bidHelp.models.User.objects.get(id=request.POST.get('ST1_id'))
    staff_st2 = bidHelp.models.User.objects.get(id=request.POST.get('ST2_id'))
    staff_ss = bidHelp.models.User.objects.get(id=request.POST.get('SS_id'))
    TS = bidHelp.models.Staff_Project(staff=staff_st1,project=project,job='TS')
    BS = bidHelp.models.Staff_Project(staff=staff_st2,project=project, job='BS')
    SS = bidHelp.models.Staff_Project(staff=staff_ss, project=project, job='SS')
    TS.save()
    BS.save()
    SS.save()
    #记录进度信息
    proccess = bidHelp.models.ProjectProccess(pID=project,proccess=state,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    proccess.save()
    #记录要求信息
    req1 = bidHelp.models.BidRequest(pID=project,rName="开标时间",rContent=request.POST.get('bidStartTime'))
    req2 = bidHelp.models.BidRequest(pID=project,rName="开标地点",rContent=request.POST.get('bidPlace'))
    req3 = bidHelp.models.BidRequest(pID=project,rName="保证金金额",rContent=request.POST.get('bankPrice'))
    req4 = bidHelp.models.BidRequest(pID=project,rName="份数要求",rContent=request.POST.get('numRes'))
    if(request.POST.get('isExpress')==1):
       req5 = bidHelp.models.BidRequest(pID=project,rName="是否邮寄",rContent='Y')
    else:
       req5 = bidHelp.models.BidRequest(pID=project, rName="是否邮寄", rContent='N')

    req6 = bidHelp.models.BidRequest(pID=project,rName="详细要求",rContent=request.POST.get('detail'))
    req1.save()
    req2.save()
    req3.save()
    req4.save()
    req5.save()
    req6.save()
    # 返回管理页面
    return adminProjectRequest(request,1,1)

def showProjectRequest(request,pID):
    project = bidHelp.models.Project.objects.get(pID=pID)
    sp_TS = bidHelp.models.Staff_Project.objects.get(job='TS',project_id=pID)
    sp_BS = bidHelp.models.Staff_Project.objects.get(job='BS', project_id=pID)
    sp_SS = bidHelp.models.Staff_Project.objects.get(job='SS', project_id=pID)
    reqs = bidHelp.models.BidRequest.objects.filter(pID_id=pID)
    context ={"project":project,"sp_TS":sp_TS,"sp_BS":sp_BS,"sp_SS":sp_SS,"reqs":reqs}
    return render(request,'bidHelp/Preparation/showProjectRequest.html',context)

def showBidRequestforST(request,uID):
    sps = bidHelp.models.Staff_Project.objects.filter(staff__uID=uID)
    projects ={}
    for sp in sps:
        projects[sp.project.id] = sp.project
    return  render(request,'bidHelp/Bidding/projectRequestListForST.html',{"projects":projects})

def tofastBidDocPage(request):
    noDocProjects = bidHelp.models.Project.objects.filter(pState_id=1)
    return render(request,'bidHelp/Bidding/fastBidDocPage.html',{"noDocProjects":noDocProjects})
