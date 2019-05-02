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
    bidResult = bidHelp.models.BidResult.objects.get(pID__pID=PID)
    return  bidResult

