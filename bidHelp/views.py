#coding=utf-8

from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import bidHelp.models
import bidHelp.Gray_model
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
    bidHelp.models.Contract.objects.create(pID=project,state=project.pState,newVerID=1)
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























