from django.db import models

class User(models.Model):
    uID = models.CharField(max_length=7)
    uName = models.CharField(max_length=10)
    uAge = models.IntegerField()
    uGender = models.CharField(max_length=2)
    uKind = models.CharField(max_length=2)
    uPassword = models.CharField(max_length=10)

class Client(models.Model):
    cID = models.CharField(max_length=10)
