#coding=utf-8

from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse, FileResponse
from django.urls import reverse
import bidHelp.models
import bidHelp.Gray_model
import bidHelp.fastGetter
from django.db.models import Q
from django.core.paginator import Paginator
import datetime
import os
import pandas as pd
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from docxtpl import DocxTemplate
from skimage import io,data
import bidHelp.Gray_model
import bidHelp.Exponential_Smooth
from django.http import JsonResponse
import zipfile


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
    projects_processNum = []
    if(user.uKind=='PJ' or user.uKind=='GM'):
        projrcts  = bidHelp.models.Project.objects.filter(pState_id__lt=21)
        for pro in projrcts:
            unit = {}
            unit['pro'] = pro
            unit['processNum'] = (int(pro.pState_id)-1)*5
            projects_processNum.append(unit)
    else:
       sps = bidHelp.models.Staff_Project.objects.filter(staff__uID=uID,project__pState_id__lt=21)
       for sp in sps:
           unit = {}
           unit['pro'] = sp.project
           unit['processNum'] = (int(sp.project.pState_id)-1)*5
           projects_processNum.append(unit)
    return render(request, 'bidHelp/index.html', {'uKind': user.uKind,'projects_processNum':projects_processNum})

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
    obj = bidHelp.models.BidInvitation.objects.get(inviteID=Iid)
    obj.bidResponse = 'N'
    obj.save()
    return toManageInvitation(request)

def adminProjectRequest(request,npIndex,rpIndex):
    noListProject = bidHelp.models.Project.objects.filter(pState=23).order_by("pID")
    np = Paginator(noListProject, 5)
    if npIndex == '':
        npIndex = '1'
    npIndex = int(npIndex)
    noListProject = np.page(npIndex)
    nplistrange = np.page_range
    readyProject = bidHelp.models.Project.objects.filter(pState_id__lt=21).order_by("pID")
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
    project.startTime = datetime.datetime().now().strftime('%Y-%m-%d')
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
    proccess = bidHelp.models.ProjectProccess(pID=project,proccess=state,time=datetime.datetime().now().strftime('%Y-%m-%d %H:%M:%S'))
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

#生成标书文件
def read_file(file_name, size):
    with open(file_name, mode='rb') as fp:
        while True:
            c = fp.read(size)
            if c:
                yield c
            else:
                break

def download_report(request,pID):
    p = bidHelp.models.Project.objects.get(pID=pID)
    try:
        data = {
            'clientName': p.inviteID.cID.cName,
            'pName':p.pName,
            'SSName':p.staff_project_set.get(job='SS').staff.uName,
            'bidTime': p.bidrequest_set.get(rName='开标时间').rContent
        }
    except Exception as e:
        return HttpResponse(_("生成文件错误"), status=status.HTTP_400_BAD_REQUEST)
        # 删除生成的报告
    filenames=['01投标函.docx','02开标一览表.docx','03投标分项报价表.docx','04法人授权书.docx',
              '05投标人资格证明.docx','06制造商资格证明.docx','07售后服务说明.docx','08营业执照副本.jpg']
    filepath = 'd:\\' + p.pName+ ' '+ datetime.datetime().now().strftime('%Y-%m-%d')
    if(os.path.exists(filepath)):
        filepath = filepath
    else:
        os.mkdir(filepath)
    for num in range(1,9):
        filename = filenames[num-1]        # 所生成的word文档需要以.docx结尾，文档格式需要
        if (num<8):
            tn = 'B0'+str(num)+'.docx'
            template_path =os.path.join(os.getcwd(),tn)
            template = DocxTemplate(template_path)
            template.render(context=data)
            template.save(os.path.join(filepath,filename))
        else:
            img = io.imread(os.path.join(os.getcwd(), 'timg.jpg'))
            io.imsave(os.path.join(filepath,filename), img)
     # time.sleep(10)
    p.bidDocPath = 'd:\\'+p.pName
    state = bidHelp.models.StateParam.objects.get(paramID=2)
    p.pState = state
    p.save()
    process = bidHelp.models.ProjectProccess.objects.create(pID=p,proccess=state,time=datetime.datetime().now().strftime('%Y-%m-%d %H:%M:%S'))
    return tofastBidDocPage(request)  #最好处理成别的跳转方式


def toBidPredictPage(request):
    devices = bidHelp.models.Device.objects.all()
    return render(request,'bidHelp/Bidding/bidPredictPage.html',{'devices':devices})

def handleBidPricePredict(request):
    device = request.GET.get('device')
    projects = bidHelp.models.Project.objects.filter(aimDevice__id=device,pState_id=21).order_by('startTime')
    pastPriceList = []
    timeList = []
    for project in projects:
        year = project.startTime.year
        month = ""
        day = ""
        if (project.startTime.month<10):
            month = "0"+str(project.startTime.month)
        else:  month = str(project.startTime.month)
        if (project.startTime.day<10):
            day = "0"+str(project.startTime.day)
        else:
            day = str(project.startTime.day)
        time = str(year)+"-"+month+"-"+day
        timeList.append(time)
        past = project.bidPrice / project.quantity
        pastPriceList.append(past)

    model = request.GET.get('model')
    if(request.GET.get('alpha')):
       alpha = float(request.GET.get('alpha'))
    pre = []
    try:
            #一阶指数平滑
            if (model=='1'):
                pre = bidHelp.Exponential_Smooth.exponential_smoothing(alpha, pastPriceList)
                pre.insert(0,pre[0])
            # 二阶指数平滑
            if(model=='2'):
                a,b  = bidHelp.Exponential_Smooth.compute_double(alpha,pastPriceList)
                pre.append(pastPriceList[0])
                for i in range(1,len(a)):
                    pre.append(a[i-1]+b[i-1])
            #三阶指数平滑
            if(model=='3'):
                a,b,c = bidHelp.Exponential_Smooth.compute_triple(alpha, pastPriceList)
                pre.append(pastPriceList[0])
                for i in range(1, len(a)):
                    pre.append( a[i-1] + b[i-1] + c[i-1])
            #GM预测
            if(model=='4'):
                    gm = bidHelp.Gray_model.Gray_model()
                    series = pd.Series(index=timeList,data=pastPriceList)
                    gm.fit(series)
                    pre = gm.predict(len(pastPriceList)).tolist()
    except Exception:
            context = {'timeList': timeList, 'past': pastPriceList}
            return JsonResponse(context)

    context = {'timeList':timeList,'past':pastPriceList,'pre':pre}
    return JsonResponse(context)

def adminBankGuarantee(request):
    uID = request.session['uID']
    user = bidHelp.models.User.objects.get(uID=uID)
    projects = []
    GuaPrices = []
    if (user.uKind == 'PJ'):
        projects = bidHelp.models.Project.objects.filter(pState__paramID__in=[2, 3])
        for project in projects:
            GuaPrices.append(bidHelp.models.BidRequest.objects.get(pID__pID=project.pID,rName='保证金金额').rContent)
    else:
        s_p = bidHelp.models.Staff_Project.objects.filter(staff__uID=uID,project__pState__paramID__in=[2,3])
        for i in range(0,len(s_p)):
            projects.append(s_p[i].project)
            GuaPrices.append(bidHelp.models.BidRequest.objects.get(pID__pID=s_p[i].project.pID,rName='保证金金额').rContent)
    pro_price = zip(projects,GuaPrices)
    return render(request,'bidHelp/Bidding/adminBankGuarantee.html',{'pro_price':pro_price})

def applyGuarantee(request,pID):
    project = bidHelp.models.Project.objects.get(pID=pID)
    project.isGuaratee = 'Y'
    ps = bidHelp.models.StateParam.objects.get(paramID=3)
    project.pState = ps
    project.save()
    bidHelp.models.ProjectProccess.objects.create(pID=project,proccess=ps,time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return adminBankGuarantee(request)

def adminBidDocCheck(request):
    uID = request.session['uID']
    user = bidHelp.models.User.objects.get(uID=uID)
    projects=[]
    if (user.uKind == 'PJ'):
        projects = bidHelp.models.Project.objects.filter(pState__paramID__in=[3,4])
    else:
        s_p = bidHelp.models.Staff_Project.objects.filter(staff__uID=uID, project__pState__paramID__in=[3,4])
        for i in range(0, len(s_p)):
            projects.append(s_p[i].project)
    bidDate = []
    for project in projects:
        bidDate.append(bidHelp.models.BidRequest.objects.get(rName='开标时间',pID__pID=project.pID).rContent)
    project_bidDate = zip(projects,bidDate)
    return render(request, 'bidHelp/Bidding/adminBidDocCheck.html', {'project_bidDate': project_bidDate})

def applyBidCheck(request,pID,bidPrice):
    project = bidHelp.models.Project.objects.get(pID=int(pID))
    ps = bidHelp.models.StateParam.objects.get(paramID=4)
    project.pState = ps
    project.bidPrice = bidPrice
    project.save()
    bidHelp.models.ProjectProccess.objects.create(pID=project, proccess=ps,
                                                  time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return adminBidDocCheck(request)

def finishBidCheck(request,pID):
    project = bidHelp.models.Project.objects.get(pID=pID)
    ps = bidHelp.models.StateParam.objects.get(paramID=5)
    project.pState = ps
    project.save()
    bidHelp.models.ProjectProccess.objects.create(pID=project, proccess=ps,
                                                  time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return adminBidDocCheck(request)

def adminBidNotice(request):
    uID = request.session['uID']
    projects = bidHelp.models.Project.objects.filter(pState_id__in=[5,6])
    DataSet = []
    for pro in projects:
        pro_bDate_bPlace_SS={}
        pro_bDate_bPlace_SS['project'] = pro
        pro_bDate_bPlace_SS['bDate'] = bidHelp.models.BidRequest.objects.get(pID__pID=pro.pID,rName='开标时间').rContent
        pro_bDate_bPlace_SS['bPlace'] = bidHelp.models.BidRequest.objects.get(pID__pID=pro.pID,rName='开标地点').rContent
        pro_bDate_bPlace_SS['SS'] = bidHelp.models.Staff_Project.objects.get(project__pID=pro.pID,job='SS').staff
        DataSet.append(pro_bDate_bPlace_SS)
    return render(request, 'bidHelp/Bidding/adminBidNotice.html', {'DataSet':DataSet})

def castBidNotice(request,pID,bidDate,bidPlace):
    project = bidHelp.models.Project.objects.get(pID=int(pID))
    preBidDate = bidHelp.models.BidRequest.objects.get(pID__pID=pID,rName='开标时间')
    preBidDate.rContent = bidDate
    preBidDate.save()
    preBidPlace = bidHelp.models.BidRequest.objects.get(pID__pID=pID,rName='开标地点')
    preBidPlace.rContent = bidPlace
    preBidPlace.save()
    state = bidHelp.models.StateParam.objects.get(paramID=6)
    project.pState = state
    project.save()
    bidHelp.models.ProjectProccess.objects.create(pID=project,proccess=state,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return HttpResponseRedirect("/adminBidNotice")

def adminBidOpen(request):
    uID = request.session['uID']
    user = bidHelp.models.User.objects.get(uID=uID)
    pro_bidTime_bidPlace=[]
    pro_SS_bidResult=[]
    if(user.uKind=='SS'):
        sps = bidHelp.models.Staff_Project.objects.filter(staff__uID=uID)
        for sp in sps:
            unit = {}
            if(sp.project.pState_id==6):
                unit['project']=sp.project
                bidTime = bidHelp.models.BidRequest.objects.get(pID__pID=sp.project.pID,rName='开标时间').rContent
                bidPlace = bidHelp.models.BidRequest.objects.get(pID__pID=sp.project.pID, rName='开标地点').rContent
                unit['bidTime'] = bidTime
                unit['bidPlace'] = bidPlace
                pro_bidTime_bidPlace.append(unit)

        return render(request,'bidHelp/BidOpen/adminBidOpen.html',{'pro_bidTime_bidPlace':pro_bidTime_bidPlace})
    else:
        projects = bidHelp.models.Project.objects.filter(pState__paramID=7)
        for pro in projects:
            unit = {}
            unit['project'] = pro
            unit['SS'] = bidHelp.models.Staff_Project.objects.get(project__pID=pro.pID,job='SS').staff
            unit['bidResult'] = bidHelp.models.BidResult.objects.get(pID__pID=pro.pID)
            pro_SS_bidResult.append(unit)

        return render(request,'bidHelp/BidOpen/adminBidOpen.html',{'pro_SS_bidResult':pro_SS_bidResult})

def reportResult_win(request,pID):
    project = bidHelp.models.Project.objects.get(pID=pID)
    state = bidHelp.models.StateParam.objects.get(paramID=7)
    project.pState=state
    project.save()
    bidHelp.models.BidResult.objects.create(pID=project,time=datetime.datetime.now().strftime('%Y-%m-%d'),isWin=True,winPrice=project.bidPrice)
    bidHelp.models.ProjectProccess.objects.create(pID=project, proccess=state,
                                                  time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return HttpResponseRedirect("/adminBidOpen")

def toLostReasonForm(request,pID):
    project = bidHelp.models.Project.objects.get(pID=pID)
    return render(request,'bidHelp/BidOpen/LostReasonForm.html',{'project':project})

def reportResult_lost(request):
    pID = request.POST.get('projectID')
    project = bidHelp.models.Project.objects.get(pID=pID)
    state = bidHelp.models.StateParam.objects.get(paramID=7)
    project.pState = state
    project.save()
    winCompany = request.POST.get('winCompany')
    winPrice = request.POST.get('winPrice')
    remark = request.POST.get('remark')
    reason = ""
    if (request.POST.get('price')=='1'):
        reason += "价格因素；"
    if (request.POST.get('technical')=='1'):
        reason += "技术设计因素；"
    if (request.POST.get('relationship')=='1'):
        reason += "客户关系因素；"
    if (request.POST.get('after-sale')=='1'):
        reason += "售后服务因素；"
    if (request.POST.get('other')=='1'):
         reason += "其他因素；"

    bidHelp.models.BidResult.objects.create(pID=project, time=datetime.datetime.now().strftime('%Y-%m-%d'), isWin=False,
                                            winPrice=winPrice,winCompany=winCompany,lostReason=reason,remark=remark)
    bidHelp.models.ProjectProccess.objects.create(pID=project, proccess=state,
                                                  time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return HttpResponseRedirect("/adminBidOpen")

def informWin(request,pID):
    project = bidHelp.models.Project.objects.get(pID=pID)
    state = bidHelp.models.StateParam.objects.get(paramID=9)
    project.pState = state
    project.save()
    bidHelp.models.ProjectProccess.objects.create(pID=project, proccess=state,
                                                  time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    bidHelp.models.Contract.objects.create(pID=project,state=project.pState,newVerID=0)
    return HttpResponseRedirect("/adminBidOpen")

def informLost (request,pID):
    project = bidHelp.models.Project.objects.get(pID=pID)
    state = bidHelp.models.StateParam.objects.get(paramID=8)
    project.pState = state
    project.endTime = datetime.datetime.now().strftime('%Y-%m-%d')
    project.save()
    bidHelp.models.ProjectProccess.objects.create(pID=project, proccess=state,
                                                  time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return HttpResponseRedirect("/adminBidOpen")

def recentBidResult(request):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(hours=71, minutes=59, seconds=59)
    recentBRSet = bidHelp.models.BidResult.objects.filter(time__gt=start)
    return render(request,'bidHelp/BidOpen/recentBidResult.html',{'recentBRSet':recentBRSet})

def searchBidResultByWord(request,searchWord):
    searchBidResultSet=[]
    if(searchWord != ""):
        searchBidResultSet = bidHelp.models.BidResult.objects.order_by('-time',).filter(Q(pID__pName__contains=searchWord)|Q(pID__inviteID__cID__cName=searchWord)|Q(pID__aimDevice__deviceID=searchWord))
    if(len(searchBidResultSet)>0):
        return render(request,'bidHelp/BidOpen/recentBidResult.html',{'searchBRSet':searchBidResultSet})
    else:
        return render(request,'bidHelp/BidOpen/recentBidResult.html',{'searchBRSet':searchBidResultSet,'remindWord ' :'noResult'})

def adminExtralRequest(request):
    uID = request.session['uID']
    uKind = bidHelp.models.User.objects.get(uID=uID).uKind
    bidResult_waitURS_yesURS_noURS =[]
    if(uKind=='PJ'):
        bidResults = bidHelp.models.BidResult.objects.filter(pID__pState__paramID=9,isWin=True)
    else:
        mys_ps = bidHelp.models.Staff_Project.objects.filter(staff__uID=uID)
        myprojectsID = []
        for mys_p in mys_ps:
            myprojectsID.append(mys_p.project.pID)
        bidResults = bidHelp.models.BidResult.objects.filter(pID__pState__paramID=9,isWin=True,pID__pID__in=myprojectsID)

    for BR in bidResults :
        unit = {}
        unit['bidResult'] = BR
        contract_id = bidHelp.models.Contract.objects.get(pID__pID=BR.pID.pID).contractID
        waitURS = bidHelp.models.ExtraRequest.objects.filter(contractID__contractID=contract_id).exclude(Q(answer='Y')|Q(answer='N'))
        unit['waitURS'] = waitURS
        yesURS = bidHelp.models.ExtraRequest.objects.filter(contractID__contractID=contract_id,answer='Y')
        unit['yesURS'] = yesURS
        noURS = bidHelp.models.ExtraRequest.objects.filter(contractID__contractID=contract_id,answer='N')
        unit['noURS'] = noURS
        bidResult_waitURS_yesURS_noURS.append(unit)

    return render(request,'bidHelp/SignContract/adminExtralRequest.html',{'bidResult_waitURS_yesURS_noURS':bidResult_waitURS_yesURS_noURS})

def addURS_Page(request,pID):
    contract = bidHelp.models.Contract.objects.get(pID__pID=pID)
    project = bidHelp.models.Project.objects.get(pID=pID)
    return render(request,'bidHelp/SignContract/addURS_Page.html',{'contract':contract,'project':project})

def addURS_handel(request):
    contractID = request.POST.get('contractID')
    requestContent = request.POST.get('requestContent')
    contract = bidHelp.models.Contract.objects.get(contractID=contractID)
    bidHelp.models.ExtraRequest.objects.create(contractID=contract,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),requestContent=requestContent)
    return HttpResponseRedirect("/adminExtralRequest")

def answerURS_Page(request):
    extralRequests = bidHelp.models.ExtraRequest.objects.order_by('time').exclude(Q(answer='Y')|Q(answer='N'))
    return render(request,'bidHelp/SignContract/answerURS_Page.html',{'extralRequests':extralRequests})

def commitURS(request,URS_ID):
    urs = bidHelp.models.ExtraRequest.objects.get(id=URS_ID)
    urs.answer = 'Y'
    urs.save()
    return HttpResponseRedirect("/answerURS_Page")

def refuseURS(request,URS_ID,reason):
    urs = bidHelp.models.ExtraRequest.objects.get(id=URS_ID)
    urs.answer = 'N'
    urs.remark =reason
    urs.save()
    return HttpResponseRedirect("/answerURS_Page")

def adminContractDoc(request):
    contracts = bidHelp.models.Contract.objects.filter(state__paramID__lt=21)
    pro_versionRecords = []
    for contract in contracts:
        unit={}
        unit['project'] = contract.pID
        versionRecords = bidHelp.models.VersionRecord.objects.filter(contractID__contractID=contract.contractID).order_by('-contractID','verID')
        unit['versionRecords'] = versionRecords
        pro_versionRecords.append(unit)
    return render(request,'bidHelp/SignContract/adminContractDoc.html',{'contracts':contracts,'pro_versionRecords':pro_versionRecords})

def uploadContract(request):  # 上传文件
    contractID = request.POST.get('uploadContractID')
    contract = bidHelp.models.Contract.objects.get(contractID = contractID)
    contract.newVerID = contract.newVerID+1
    contract.save()
    if request.method == 'POST':
        try:
            handle_uploaded_file(request.FILES.get("file-input", None),contract.pID.pName,contract.newVerID)
            path = contract.pID.pName+'_第'+ str(contract.newVerID) +'版合同.zip'
            bidHelp.models.VersionRecord.objects.create(contractID=contract,verID=contract.newVerID,docPath=path,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return HttpResponseRedirect('/adminContractDoc')
        except Exception:
            return HttpResponseRedirect('/adminContractDoc')
    return HttpResponseRedirect('/adminContractDoc')

def handle_uploaded_file(file,pName,verID):
    if not os.path.exists('upload/'):
        os.mkdir('upload/')
        # print file.name
    with open('upload/' + pName+'_第'+ str(verID) +'版合同.zip', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()


def downLoadFirstVersionContract(request,conID):
    def file_iterator(file_name, chunk_size=512):
        print(file_name, '******************')
        with open(file_name, 'rb') as f:
            if f:
                yield f.read(chunk_size)
                print('下载完成')
            else:
                print('未完成下载')
    the_file_name = 'E:/biddingMIS/upload/firstVersionContract.zip'
    contract = bidHelp.models.Contract.objects.get(contractID = conID)
    if(contract.newVerID==0):
        contract.newVerID=1
        contract.save()
        bidHelp.models.VersionRecord.objects.create(contractID = contract,verID=1,docPath='firstVersionContract.zip',time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="firstVersionContract.zip"'
    else:
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="firstVersionContract.zip"'
    return response

def downloadFile(request,path):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name, 'rb') as f:
            if f:
                yield f.read(chunk_size)
                print('下载完成')
            else:
                print('未完成下载')
    response = StreamingHttpResponse(file_iterator('E:/biddingMIS/upload/'+path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachement;'
    return response

def toContractCheck(request):
    uID = request.session.get('uID')
    user = bidHelp.models.User.objects.get(uID=uID)
    if(user.uKind=='PJ' or user.uKind=='GM'):
        contracts = bidHelp.models.Contract.objects.filter(state__paramID__in=[9,10,11,12])
    else:
        personalPro = bidHelp.fastGetter.getProjectsByUID(uID)
        myProID = []
        for myPro in personalPro:
            myProID.append(myPro.pID)
        contracts = bidHelp.models.Contract.objects.filter(pID__pID__in=myProID,state__paramID__in=[9,10,11,12])

    contract_processes = []
    for con in contracts:
        unit={}
        unit['contract'] = con
        processes = bidHelp.models.ProjectProccess.objects.filter(pID__pID=con.pID.pID,proccess__paramID__in=[10,11,12])
        unit['processes'] = processes
        contract_processes.append(unit)
    return  render(request, 'bidHelp/SignContract/contractCheckPage.html',{'contract_processes':contract_processes})

def applyForFirstCheck(request,conID,finalverID,contractPrice,firTimeSpan,firPartPrice,productTime,secTimeSpan,secPartPrice,conveyTime,thrTimeSpan,thrPartPrice):
    contract = bidHelp.models.Contract.objects.get(contractID=conID)
    contract.newVerID = finalverID
    contract.contractDocPath = bidHelp.models.VersionRecord.objects.get(contractID__contractID=conID,verID=finalverID).docPath
    contract.contractPrice = contractPrice
    contract.firPartPrice = firPartPrice
    contract.firTimeSpan = firTimeSpan
    contract.productTime = productTime
    contract.secTimeSpan = secTimeSpan
    contract.secPartPrice = secPartPrice
    contract.thrTimeSpan = thrTimeSpan
    contract.thrPartPrice = thrPartPrice
    contract.conveyTime = conveyTime
    state = bidHelp.models.StateParam.objects.get(paramID=10)
    contract.state = state
    contract.pID.pState = state
    contract.save()
    contract.pID.save()
    bidHelp.models.ProjectProccess.objects.create(pID=contract.pID,proccess=state,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return  HttpResponseRedirect('/toContractCheck')

def contractFirstSign(request,conID):
    contract = bidHelp.models.Contract.objects.get(contractID=conID)
    changeState = bidHelp.models.StateParam.objects.get(paramID=11)
    contract.state = changeState
    contract.pID.pState = changeState
    contract.pID.save()
    contract.save()
    bidHelp.models.ProjectProccess.objects.create(pID=contract.pID,proccess=changeState,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return  HttpResponseRedirect('/toContractCheck')

def contractSecondSign(request,conID):
    contract = bidHelp.models.Contract.objects.get(contractID=conID)
    changeState = bidHelp.models.StateParam.objects.get(paramID=12)
    contract.state = changeState
    contract.pID.pState = changeState
    contract.pID.save()
    contract.save()
    bidHelp.models.ProjectProccess.objects.create(pID=contract.pID,proccess=changeState,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return  HttpResponseRedirect('/toContractCheck')

def receiveSignedContract(request,conID):
    contract = bidHelp.models.Contract.objects.get(contractID=conID)
    changeState = bidHelp.models.StateParam.objects.get(paramID=13)
    contract.state = changeState
    contract.pID.pState = changeState
    contract.pID.save()
    contract.signTime = datetime.datetime.now().strftime('%Y-%m-%d')
    contract.save()
    bidHelp.models.ProjectProccess.objects.create(pID=contract.pID, proccess=changeState,
                                                  time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return HttpResponseRedirect('/adminReceiveMoney')

def adminReceiveMoney(request):
    projects = bidHelp.models.Project.objects.filter(pState__paramID__in = [13,14,15,16,17,18,19])
    pro_contract_processInfor = []
    for project in projects:
        unit = {}
        contract = bidHelp.fastGetter.getContractByPID(project.pID)
        unit['pro'] = project
        unit['contract'] = contract
        firMoneyAmount = int(contract.contractPrice) * int(contract.firPartPrice) / 100
        secMoneyAmount = int(contract.contractPrice) * int(contract.secPartPrice) / 100
        thrMoneyAmount = int(contract.contractPrice) * int(contract.thrPartPrice) / 100
        oneAndTwoMoneyAmount = firMoneyAmount + secMoneyAmount
        print(project.pState.paramID)
        if(project.pState.paramID==13):
            timeLimit =(contract.signTime+datetime.timedelta(days=contract.firTimeSpan)).strftime('%Y{y}%m{m}%d{d}').format(y='年',m='月',d='日')
            processInfor = '<p>未收款</p><p style = "color:blue">于'+timeLimit+'前，应支付首期货款：¥'+str(firMoneyAmount)+'</p>'
            unit['processInfor'] = processInfor
        elif(project.pState.paramID > 13 and project.pState.paramID <16):
            processInfor = '<p>已收首期款，共¥'+str(firMoneyAmount)+'</p><p>正在生产中，等待FAT验收</p>'
            unit['processInfor'] = processInfor
        elif(project.pState.paramID==16):
            overFATTime = bidHelp.models.ProjectProccess.objects.get(pID__pID=project.pID,proccess__paramID=16).time
            timeLimit =(overFATTime+datetime.timedelta(days=contract.secTimeSpan)).strftime('%Y{y}%m{m}%d{d}').format(y='年',m='月',d='日')
            processInfor ='<p>已收首期款，共¥'+str(firMoneyAmount)+'</p><p style = "color:blue">于'+timeLimit+'前，应支付中期货款：¥'+str(secMoneyAmount)+'</p>'
            unit['processInfor'] = processInfor
        elif(project.pState.paramID > 16 and project.pState.paramID < 19):
            processInfor = '<p>已收中期款，共¥'+str(oneAndTwoMoneyAmount)+'</p><p>正在运输中，等待SAT验收</p>'
            unit['processInfor'] = processInfor
        elif(project.pState.paramID==19):
            overSATTime = bidHelp.models.ProjectProccess.objects.get(pID__pID=project.pID,proccess__paramID=19).time
            timeLimit =(overSATTime+datetime.timedelta(days=contract.thrTimeSpan)).strftime('%Y{y}%m{m}%d{d}').format(y='年',m='月',d='日')
            processInfor ='<p>已收中期款，共¥'+str(oneAndTwoMoneyAmount)+'</p><p style = "color:blue">于'+timeLimit+'前，应支付尾款：¥'+str(thrMoneyAmount)+'</p>'
            unit['processInfor'] = processInfor

        pro_contract_processInfor.append(unit)

    return  render(request,'bidHelp/ExerciseAgreement/adminReceiveMoney.html',{'pro_contract_processInfor':pro_contract_processInfor})

def reciveMoney(request,conID,type):
    contract = bidHelp.models.Contract.objects.get(contractID=conID)
    changeState = bidHelp.models.StateParam.objects.get(paramID=contract.state.paramID+1)
    contract.state = changeState
    contract.pID.pState = changeState
    contract.save()
    contract.pID.save()
    bidHelp.models.ProjectProccess.objects.create(pID=contract.pID,proccess=changeState,time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
    if(type=='t1'):
         return HttpResponseRedirect('/adminReceiveMoney')
    else:
        return HttpResponseRedirect('/adminProductConvey')

def adminProductConvey(request):
    projects = bidHelp.models.Project.objects.filter(pState__paramID__in=[14, 15, 16, 17, 18])
    pro_contract_processInfor = []
    for project in projects:
        unit = {}
        contract = bidHelp.fastGetter.getContractByPID(project.pID)
        unit['pro'] = project
        unit['contract'] = contract
        if (project.pState.paramID == 14):
            timeLimit = (contract.signTime + datetime.timedelta(days=contract.productTime)).strftime(
                '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
            processInfor = '<p>生产进行中</p><p style = "color:blue">于' + timeLimit + '前，申请进行FAT验收</p>'
            unit['processInfor'] = processInfor
        elif (project.pState.paramID ==15):
            processInfor = '<p>FAT验收中，验收结束后请上传相应FAT验收文件</p>'
            unit['processInfor'] = processInfor
        elif (project.pState.paramID == 17):
            time = bidHelp.models.ProjectProccess.objects.get(pID__pID=project.pID,proccess__paramID=17).time
            timeLimit = (time + datetime.timedelta(days=contract.conveyTime)).strftime(
                '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
            processInfor = '<p>运输进行中</p><p style = "color:blue">于' + timeLimit + '前完成运输安装并开始SAT验收</p>'
            unit['processInfor'] = processInfor
        elif (project.pState.paramID == 18):
            processInfor = '<p>SAT验收中，验收结束后请上传相应SAT验收文件</p>'
            unit['processInfor'] = processInfor
        elif (project.pState.paramID == 16):
            processInfor = '<p>完成FAT验收，请客户交付中期货款</p>'
            unit['processInfor'] = processInfor

        pro_contract_processInfor.append(unit)
    return  render(request,'bidHelp/ExerciseAgreement/adminProductConvey.html',{'pro_contract_processInfor':pro_contract_processInfor})


def uploadAcceptenceDoc(request,conID):
    contract = bidHelp.models.Contract.objects.get(contractID=conID)
    try:
        if(contract.state.paramID == 15):
            file = request.FILES.get("FATDoc")
            f = zipfile.ZipFile(file, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=False)
            zipfilename = contract.pID.pName+'_FAT验收文件.zip'
            contract.FATDoc = zipfilename
            with open('upload/' + zipfilename, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                destination.close()
        else:
            file = request.FILES.get("SATDoc")
            f = zipfile.ZipFile(file, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=False)
            zipfilename = contract.pID.pName+'_SAT验收文件.zip'
            contract.SATDoc = zipfilename
            with open('upload/' + zipfilename, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                destination.close()

        changeState = bidHelp.models.StateParam.objects.get(paramID=contract.state.paramID + 1)
        contract.state = changeState
        contract.pID.pState = changeState
        contract.save()
        contract.pID.save()
        bidHelp.models.ProjectProccess.objects.create(pID=contract.pID, proccess=changeState,
                                                      time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return HttpResponseRedirect('/adminProductConvey')
    except Exception:
        return HttpResponseRedirect('/adminProductConvey')#考虑报错

def adminWarning(request):
    projects = bidHelp.models.Project.objects.exclude(pState__paramID__in =[20,21])
    pro_alarmKind_predate_date= []
    for project in projects:
        unit={}
        unit['project'] = project
        if(project.pState_id < 5 or project.pState_id==23):
            pre_bidOpenTime = bidHelp.models.BidRequest.objects.get(pID__pID=project.pID,rName='开标时间').rContent
            pre_bidOpenTime = datetime.datetime.strptime(pre_bidOpenTime, "%Y-%m-%d")
            delta = (pre_bidOpenTime - datetime.datetime.now()).days
            unit['predate'] = pre_bidOpenTime
            if(delta>0 and delta<3):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=1)
                unit['date'] = delta
            elif(delta<0):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=11)
                unit['date'] = abs(delta)

            if (unit['date']>0):
                pro_alarmKind_predate_date.append(unit)

        elif(project.pState_id>=5 and project.pState_id<14 and bidHelp.fastGetter.getBidResultByPID(project.pID).isWin==True):
            contract = bidHelp.fastGetter.getContractByPID(project.pID)
            signTime = contract.signTime
            if(signTime!=""):
                timeSpan= datetime.timedelta(days=contract.firTimeSpan)
                pre_firstPriceDate = signTime+timeSpan
                unit['predate'] = pre_firstPriceDate
                delta = pre_firstPriceDate - datetime.datetime.now()
                if (delta > 0 and delta < 3):
                    unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=2)
                    unit['date'] = delta
                elif (delta < 0):
                    unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=12)
                    unit['date'] = abs(delta)

                if (unit['date'] > 0):
                    pro_alarmKind_predate_date.append(unit)

        elif (project.pState_id == 14):
            contract = bidHelp.fastGetter.getContractByPID(project.pID)
            timeSpan = datetime.timedelta(days=contract.productTime)
            pre_FATTime=bidHelp.models.ProjectProccess.objects.get(pID__pID=project.id,proccess__paramID=14).time+timeSpan
            unit['predate'] = pre_FATTime
            delta = pre_FATTime - datetime.datetime.now()
            if (delta > 0 and delta < 3):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=3)
                unit['date'] = delta
            elif (delta < 0):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=13)
                unit['date'] = abs(delta)

            if (unit['date']>0):
                pro_alarmKind_predate_date.append(unit)

        elif(project.pState_id==16):
            contract = bidHelp.fastGetter.getContractByPID(project.pID)
            timeSpan = datetime.timedelta(days=contract.secTimeSpan)
            pre_secPriceDate = bidHelp.models.ProjectProccess.objects.get(pID__pID=project.id,
                                                                     proccess__paramID=16).time + timeSpan
            unit['predate'] = pre_secPriceDate
            delta = pre_secPriceDate - datetime.datetime.now()
            if (delta > 0 and delta < 3):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=4)
                unit['date'] = delta
            elif (delta < 0):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=14)
                unit['date'] = abs(delta)

            if (unit['date']>0):
                pro_alarmKind_predate_date.append(unit)

        elif(project.pState_id==17):
            contract = bidHelp.fastGetter.getContractByPID(project.pID)
            timeSpan = datetime.timedelta(days=contract.conveyTime)
            pre_SATTime = bidHelp.models.ProjectProccess.objects.get(pID__pID=project.id,
                                                                          proccess__paramID=17).time + timeSpan
            unit['predate'] = pre_SATTime
            delta = pre_SATTime - datetime.datetime.now()
            if (delta > 0 and delta < 3):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=5)
                unit['date'] = delta
            elif (delta < 0):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=15)
                unit['date'] = abs(delta)

            if (unit['date']>0):
                pro_alarmKind_predate_date.append(unit)

        elif(project.pState_id==19):
            contract = bidHelp.fastGetter.getContractByPID(project.pID)
            timeSpan = datetime.timedelta(days=contract.thrTimeSpan)
            pre_thrPriceDate = bidHelp.models.ProjectProccess.objects.get(pID__pID=project.id,
                                                                          proccess__paramID=19).time + timeSpan
            unit['predate'] = pre_thrPriceDate
            delta = pre_thrPriceDate - datetime.datetime.now()
            if (delta > 0 and delta < 3):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=6)
                unit['date'] = delta
            elif (delta < 0):
                unit['alarmKind'] = bidHelp.models.AiarmParam.objects.get(apID=16)
                unit['date'] = abs(delta)

            if (unit['date']>0):
                pro_alarmKind_predate_date.append(unit)
    return render(request,'bidHelp/ExerciseAgreement/alarmPage.html',{'pro_alarmKind_predate_date':pro_alarmKind_predate_date})

def overProject(request,pID):
    project  = bidHelp.models.Project.objects.get(pID=pID)
    changeState = bidHelp.models.StateParam.objects.get(paramID=21)
    contract = bidHelp.fastGetter.getContractByPID(pID)
    contract.state = changeState
    project.pState = changeState
    project.save()
    contract.save()
    return HttpResponseRedirect('/index')

def breakUpProject(request,pID):
    project  = bidHelp.models.Project.objects.get(pID=pID)
    changeState = bidHelp.models.StateParam.objects.get(paramID=24)
    project.pState = changeState
    project.save()
    try:
        if bidHelp.fastGetter.getContractByPID(pID):
            bidHelp.fastGetter.getContractByPID(pID).state=changeState
            bidHelp.fastGetter.getContractByPID(pID).save()
    except Exception:
        print('无合同')
    return HttpResponseRedirect('/index')

























