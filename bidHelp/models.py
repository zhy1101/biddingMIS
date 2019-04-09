from django.db import models

class User(models.Model):
    uName = models.CharField(max_length=10)
