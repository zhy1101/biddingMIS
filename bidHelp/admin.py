from django.contrib import admin
import bidHelp.models as models

admin.site.register(models.User)
admin.site.register(models.Customer)
admin.site.register(models.BidInvitation)
admin.site.register(models.StateParam)
admin.site.register(models.Device)
admin.site.register(models.Project)
admin.site.register(models.Staff_Project)
admin.site.register(models.BidRequest)
admin.site.register(models.BidResult)
admin.site.register(models.Contract)
admin.site.register(models.ExtraRequest)
admin.site.register(models.VersionRecord)
admin.site.register(models.AiarmParam)
admin.site.register(models.Alarm)
admin.site.register(models.ProjectProccess)



