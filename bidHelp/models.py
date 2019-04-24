from django.db import models

class User(models.Model):
    uID = models.CharField(max_length=7,null=True)
    uName = models.CharField(max_length=10,null=True)
    uAge = models.IntegerField(null=True)
    uGender = models.CharField(max_length=2,null=True)
    uKind = models.CharField(max_length=2,null=True)
    uPassword = models.CharField(max_length=10,null=True)
    uPhone = models.CharField(max_length=20,null=True)
    uWorkTime = models.IntegerField(null=True)

class Customer(models.Model):
    cID = models.AutoField(primary_key=True)
    cName = models.CharField(max_length=50,null=True)
    cEnglishName = models.CharField(max_length=100,null=True)
    cAddress = models.CharField(max_length=80,null=True)
    cContactPerson = models.CharField(max_length=20,null=True)
    cPhone = models.CharField(max_length=20,null=True)

class BidInvitation(models.Model):
    inviteID = models.AutoField(primary_key=True)
    inviteTime = models.DateField(null=True)
    inviteName = models.CharField(max_length=30,null=True)
    inviteContent = models.TextField(null=True)
    endTime = models.DateTimeField(null=True)
    resWay = models.CharField(max_length=200,null=True)
    preBidTime = models.DateField(null=True)
    response = models.CharField(max_length=2,null=True)
    cID = models.ForeignKey(Customer,on_delete=models.CASCADE)

class StateParam(models.Model):
    paramID = models.AutoField(primary_key=True)
    paramContent = models.CharField(max_length=100,null=True)
    remark = models.CharField(max_length=20,null=True)

class Device(models.Model):
    deviceName = models.CharField(max_length=20,null=True)
    deviceID = models.CharField(max_length=200,null=True)
    functionWord = models.CharField(max_length=100,null=True)
    picPath = models.TextField(null=True)

class Project(models.Model):
    pID = models.AutoField(primary_key=True)
    inviteID = models.ForeignKey(BidInvitation,on_delete=models.CASCADE,null=True)
    pName = models.CharField(max_length=40,null=True)
    startTime = models.DateField(null=True)
    endTime = models.DateField(null=True)
    bidPrice = models.IntegerField(null=True)
    pState = models.ForeignKey(StateParam,on_delete=models.CASCADE,null=True)
    bidDocPath = models.TextField(null=True)
    remark = models.CharField(max_length=100,null=True)
    isGuaratee = models.CharField(max_length=2,null=True)
    aimDevice = models.ForeignKey(Device, on_delete=models.CASCADE,null=True)
    currentKind = models.CharField(max_length=3,null=True)
    quantity = models.IntegerField(null=True)

class Staff_Project(models.Model):
    staff = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    job = models.CharField(max_length=2,null=True)


class BidRequest(models.Model):
    rID = models.AutoField(primary_key=True)
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    rKind = models.CharField(max_length=2,null=True)
    rName = models.CharField(max_length=30,null=True)
    rContent = models.CharField(max_length=100,null=True)


class BidResult(models.Model):
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    time = models.DateField(auto_now_add=True)
    isWin = models.BooleanField(null=True)
    winPrice = models.IntegerField(null=True)
    winCompany = models.CharField(max_length=30,null=True)
    lostReason = models.CharField(max_length=30,null=True)
    remark = models.CharField(max_length=100,null=True)

class Contract(models.Model):
    contractID = models.AutoField(primary_key=True)
    pID = models.ForeignKey(Project,on_delete=models.CASCADE,null=True)
    state = models.ForeignKey(StateParam,on_delete=models.CASCADE,null=True)
    newVerID = models.IntegerField(null=True)
    contractDocPath = models.TextField(null=True)
    contractPrice = models.IntegerField(null=True)
    firPartPrice = models.DecimalField(max_digits = 3,decimal_places = 2,null=True)
    secPartPrice = models.DecimalField(max_digits=3, decimal_places=2,null=True)
    thrPartPrice = models.DecimalField(max_digits = 3,decimal_places = 2,null=True)
    firTimeSpan = models.IntegerField(null=True)
    secTimeSpan = models.IntegerField(null=True)
    thrTimeSpan = models.IntegerField(null=True)
    productTime = models.IntegerField(null=True)
    conveyTime = models.IntegerField(null=True)
    FATDoc = models.TextField(null=True)
    SATDoc = models.TextField(null=True)
    signTime = models.DateField(null=True)

class ExtraRequest(models.Model):
    contractID = models.ForeignKey(Contract,on_delete=models.CASCADE,null=True)
    time = models.DateTimeField(auto_now_add=True,null=True)
    requestContent = models.TextField(null=True)
    answer = models.CharField(max_length=2,null=True)
    remark = models.TextField(null=True)

class VersionRecord(models.Model):
    contractID = models.ForeignKey(Contract,on_delete=models.CASCADE,null=True)
    verID = models.IntegerField(null=True)
    docPath = models.TextField(null=True)
    time = models.DateTimeField(auto_now_add=True,null=True)

class AiarmParam(models.Model):
    apID = models.AutoField(primary_key=True)
    aContent = models.CharField(max_length=20,null=True)

class Alarm(models.Model):
    time = models.DateTimeField(auto_now_add=True,null=True)
    aKind = models.ForeignKey(AiarmParam,on_delete=models.CASCADE,null=True)
    aState = models.CharField(max_length=10,null=True)
    exDay = models.IntegerField(null=True)

class ProjectProccess(models.Model):
    pID = models.ForeignKey(Project,on_delete=models.CASCADE,null=True)
    proccess = models.ForeignKey(StateParam,on_delete=models.CASCADE,null=True)
    time = models.DateTimeField(auto_now_add=True,null=True)



