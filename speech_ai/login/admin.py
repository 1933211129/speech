from django.contrib import admin
from . import models

admin.site.register(models.MyUser)
admin.site.register(models.Pose)
admin.site.register(models.Speach)