from django.db import models

class User(models.Model):
    uID = models.CharField(max_length=7,blank=True)
    uName = models.CharField(max_length=10,blank=True)
    uAge = models.IntegerField(blank=True)
    uGender = models.CharField(max_length=2,blank=True)
    uKind = models.CharField(max_length=2,blank=True)
    uPassword = models.CharField(max_length=10,blank=True)
    uPhone = models.CharField(max_length=20,blank=True)
    uWorkTime = models.IntegerField(blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_user'

class Customer(models.Model):
    cID = models.AutoField(primary_key=True)
    cName = models.CharField(max_length=50,blank=True)
    cEnglishName = models.CharField(max_length=100,blank=True)
    cAddress = models.CharField(max_length=80,blank=True)
    cContactPerson = models.CharField(max_length=20,blank=True)
    cPhone = models.CharField(max_length=20,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_customer'

class BidInvitation(models.Model):
    inviteID = models.AutoField(primary_key=True)
    inviteTime = models.DateField(blank=True)
    inviteName = models.CharField(max_length=30,blank=True)
    inviteContent = models.TextField(blank=True)
    endTime = models.DateTimeField(blank=True)
    resWay = models.CharField(max_length=200,blank=True)
    preBidTime = models.DateField(blank=True)
    bidResponse = models.CharField(max_length=2,blank=True)
    cID = models.ForeignKey(Customer,on_delete=models.CASCADE)
    class Meta:
        managed = True
        db_table = 'bidhelp_bidinvitation'

class StateParam(models.Model):
    paramID = models.AutoField(primary_key=True)
    paramContent = models.CharField(max_length=100,blank=True)
    remark = models.CharField(max_length=20,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_stateparam'

class Device(models.Model):
    deviceName = models.CharField(max_length=20,blank=True)
    deviceID = models.CharField(max_length=200,blank=True)
    functionWord = models.CharField(max_length=100,blank=True)
    picPath = models.TextField(blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_device'

class Project(models.Model):
    pID = models.AutoField(primary_key=True)
    inviteID = models.ForeignKey(BidInvitation,on_delete=models.CASCADE)
    pName = models.CharField(max_length=40,blank=True)
    startTime = models.DateField(blank=True)
    endTime = models.DateField(blank=True)
    bidPrice = models.IntegerField(blank=True)
    pState = models.ForeignKey(StateParam,on_delete=models.CASCADE)
    bidDocPath = models.TextField(blank=True)
    remark = models.CharField(max_length=100,blank=True)
    isGuaratee = models.CharField(max_length=2,blank=True)
    aimDevice = models.ForeignKey(Device, on_delete=models.CASCADE)
    currentKind = models.CharField(max_length=3,blank=True)
    quantity = models.IntegerField(blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_project'

class Staff_Project(models.Model):
    staff = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    job = models.CharField(max_length=2,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_staff_project'


class BidRequest(models.Model):
    rID = models.AutoField(primary_key=True)
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    rKind = models.CharField(max_length=2,blank=True)
    rName = models.CharField(max_length=30,blank=True)
    rContent = models.CharField(max_length=100,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_bidrequest'


class BidResult(models.Model):
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    time = models.DateField(auto_now_add=True,blank=True)
    isWin = models.BooleanField(blank=True)
    winPrice = models.IntegerField(blank=True)
    winCompany = models.CharField(max_length=30,blank=True)
    lostReason = models.CharField(max_length=30,blank=True)
    remark = models.CharField(max_length=100,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_bidresult'

class Contract(models.Model):
    contractID = models.AutoField(primary_key=True)
    pID = models.ForeignKey(Project,on_delete=models.CASCADE)
    state = models.ForeignKey(StateParam,on_delete=models.CASCADE)
    newVerID = models.IntegerField(blank=True)
    contractDocPath = models.TextField(blank=True)
    contractPrice = models.IntegerField(blank=True)
    firPartPrice = models.DecimalField(max_digits = 3,decimal_places = 2,blank=True)
    secPartPrice = models.DecimalField(max_digits=3, decimal_places=2,blank=True)
    thrPartPrice = models.DecimalField(max_digits = 3,decimal_places = 2,blank=True)
    firTimeSpan = models.IntegerField(blank=True)
    secTimeSpan = models.IntegerField(blank=True)
    thrTimeSpan = models.IntegerField(blank=True)
    productTime = models.IntegerField(blank=True)
    conveyTime = models.IntegerField(blank=True)
    FATDoc = models.TextField(blank=True)
    SATDoc = models.TextField(blank=True)
    signTime = models.DateField(blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_contract'

class ExtraRequest(models.Model):
    contractID = models.ForeignKey(Contract,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True,blank=True)
    requestContent = models.TextField(blank=True)
    answer = models.CharField(max_length=2,blank=True)
    remark = models.TextField(blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_extrarequest'

class VersionRecord(models.Model):
    contractID = models.ForeignKey(Contract,on_delete=models.CASCADE)
    verID = models.IntegerField(blank=True)
    docPath = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_versionrecord'

class AiarmParam(models.Model):
    apID = models.AutoField(primary_key=True)
    aContent = models.CharField(max_length=20,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_aiarmparam'

class Alarm(models.Model):
    time = models.DateTimeField(auto_now_add=True,blank=True)
    aKind = models.ForeignKey(AiarmParam,on_delete=models.CASCADE)
    aState = models.CharField(max_length=10,blank=True)
    exDay = models.IntegerField(blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_alarm'

class ProjectProccess(models.Model):
    pID = models.ForeignKey(Project,on_delete=models.CASCADE,blank=True)
    proccess = models.ForeignKey(StateParam,on_delete=models.CASCADE,blank=True)
    time = models.DateTimeField(auto_now_add=True,blank=True)
    class Meta:
        managed = True
        db_table = 'bidhelp_projectproccess'


