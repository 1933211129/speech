from django.db import models

# Create your models here.
from django.db import models

class Visit(models.Model):
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    ip_address = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255)
    response_time = models.FloatField() # 毫秒
    time_stamp = models.FloatField(default=0)
    bytes_send = models.IntegerField(default=0)
    bytes_recv = models.IntegerField(default=0)

    # class Meta:
    #     db_table = 'visit'
