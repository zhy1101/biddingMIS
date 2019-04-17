from django.db import models

class User(models.Model):
    uID = models.CharField(max_length=7)
    uName = models.CharField(max_length=10)
    uAge = models.IntegerField()
    uGender = models.CharField(max_length=2)
    uKind = models.CharField(max_length=2)
    uPassword = models.CharField(max_length=10)
    uPhone = models.CharField(max_length=20)
    uWorkTime = models.IntegerField

class Customer(models.Model):
    cID = models.AutoField(primary_key=True)
    cName = models.CharField(max_length=50)
    cEnglishName = models.CharField(max_length=100)
    cAddress = models.CharField(max_length=80)
    cContactPerson = models.CharField(max_length=20)
    cPhone = models.CharField(max_length=20)

class BidInvitation(models.Model):
    inviteID = models.AutoField(primary_key=True)
    inviteTime = models.DateField
    inviteName = models.CharField(max_length=30)
    inviteContent = models.TextField
    endTime = models.DateTimeField
    resWay = models.CharField(max_length=200)
    preBidTime = models.DateField
    response = models.CharField(max_length=2)
    cID = models.ForeignKey(Customer,on_delete=models.CASCADE)

class StateParam(models.Model):
    paramID = models.AutoField(primary_key=True)
    paramContent = models.CharField(max_length=100)
    remark = models.CharField(max_length=20)

class Project(models.Model):
    pID = models.AutoField(primary_key=True)
    inviteID = models.ForeignKey(BidInvitation,on_delete=models.CASCADE)
    pName = models.CharField(max_length=40)
    startTime = models.DateField
    endTime = models.DateField
    bidPrice = models.IntegerField
    pState = models.ForeignKey(StateParam,on_delete=models.CASCADE)
    bidDocPath = models.TextField
    remark = models.CharField(max_length=100)
    isGuaratee = models.CharField(max_length=2)

class Staff_Project(models.Model):
    staff = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    job = models.CharField(max_length=2)

class Device(models.Model):
    deviceName = models.CharField(max_length=20)
    deviceID = models.CharField(max_length=10)
    functionWord = models.CharField(max_length=100)
    picPath = models.TextField

class BidRequest(models.Model):
    rID = models.AutoField(primary_key=True)
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    rKind = models.CharField(max_length=2)
    rName = models.CharField(max_length=30)
    rContent = models.CharField(max_length=100)
    aimDevice = models.ForeignKey(Device,on_delete=models.CASCADE)

class BidResult(models.Model):
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    time = models.DateField(auto_now_add=True)
    isWin = models.BooleanField
    winPrice = models.IntegerField
    winCompany = models.CharField(max_length=30)
    lostReason = models.CharField(max_length=30)
    remark = models.CharField(max_length=100)

class Contract(models.Model):
    contractID = models.AutoField(primary_key=True)
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    state = models.ForeignKey(StateParam,on_delete=models.CASCADE)
    newVerID = models.IntegerField
    contractDocPath = models.TextField
    contractPrice = models.IntegerField
    firPartPrice = models.DecimalField(max_digits = 3,decimal_places = 2)
    secPartPrice = models.DecimalField(max_digits=3, decimal_places=2)
    thrPartPrice = models.DecimalField(max_digits = 3,decimal_places = 2)
    firTimeSpan = models.IntegerField
    secTimeSpan = models.IntegerField
    thrTimeSpan = models.IntegerField
    productTime = models.IntegerField
    conveyTime = models.IntegerField
    FATDoc = models.TextField
    SATDoc = models.TextField
    signTime = models.DateField

class ExtraRequest(models.Model):
    contractID = models.ForeignKey(Contract,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    requestContent = models.TextField
    answer = models.CharField(max_length=2)
    remark = models.TextField

class VersionRecord(models.Model):
    contractID = models.ForeignKey(Contract,on_delete=models.CASCADE)
    verID = models.IntegerField
    docPath = models.TextField
    time = models.DateTimeField(auto_now_add=True)

class AiarmParam(models.Model):
    apID = models.AutoField(primary_key=True)
    aContent = models.CharField(max_length=20)

class Alarm(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    aKind = models.ForeignKey(AiarmParam,on_delete=models.CASCADE)
    aState = models.CharField(max_length=10)
    exDay = models.IntegerField

class ProjectProccess(models.Model):
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    proccess = models.ForeignKey(StateParam,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)


