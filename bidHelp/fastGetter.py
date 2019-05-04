from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import bidHelp.models

def getProjectsByUID(uID):
    sps = bidHelp.models.Staff_Project.objects.filter(staff__uID=uID)
    myprojects = []
    for sp in sps:
        myprojects.append(sp.project)
    return myprojects

def getContractByPID(pID):
    contract = bidHelp.models.Contract.objects.get(pID__pID=pID)
    return contract

def getBidResultByPID(PID):
    bidResult = bidHelp.models.BidResult.objects.filter(pID__pID=PID)
    return  bidResult[0]

def getCustomerBypID(pID):
    return bidHelp.models.Project.objects.get(pID=pID).inviteID.cID

def getBidResultByPID(pID):
    result = bidHelp.models.BidResult.objects.filter(pID__pID=pID)
    try:
        if(result[0].isWin):
            return 1
        else:
            return 0
    except:
        return 0

def lostReasonisPrice(pID):
    reason = bidHelp.models.BidResult.objects.filter(pID__pID=pID,lostReason__contains='标价')
    if len(reason)< 1:
        return 0
    else:
        return 1

def lostReasonisTec(pID):
    reason = bidHelp.models.BidResult.objects.filter(pID__pID=pID,lostReason__contains='技术')
    if len(reason)< 1:
        return 0
    else:
        return 1

def lostReasonisRelation(pID):
    reason = bidHelp.models.BidResult.objects.filter(pID__pID=pID,lostReason__contains='关系')
    if len(reason)< 1:
        return 0
    else:
        return 1

def lostReasonisAftersale(pID):
        reason = bidHelp.models.BidResult.objects.filter(pID__pID=pID, lostReason__contains='售后')
        if len(reason) < 1:
            return 0
        else:
            return 1


def lostReasonisOther(pID):
    reason = bidHelp.models.BidResult.objects.filter(pID__pID=pID, lostReason__contains='其他')
    if len(reason) < 1:
        return 0
    else:
        return 1

def getProjectsBycID(cID):
    projects = bidHelp.models.Project.objects.filter(inviteID__cID=cID)
    return projects


