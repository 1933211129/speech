from django.db import models


class ip_list(models.Model):
    # ip不重复
    ip = models.CharField(max_length=16,unique=True)
    frequency = models.DecimalField(max_digits=3, decimal_places=2,default=0)
    intercept_choices = (
        (1, "Black"),
        (0, "White"),
        (2, "Temporary"),
        (3,"None")
    )
    status = models.SmallIntegerField(choices=intercept_choices)
    description = models.CharField(max_length=64,default="暂无")



class Black_List(models.Model):
    """ 临时ip黑名单"""
    """可保留同一ip被封禁多次的记录"""

    ip = models.CharField(max_length=16)

    prohibit_time = models.DateTimeField(max_length=32)
    # 起封日期
    # 解封日期
    access_time = models.DateTimeField(max_length=32)
    prohibit_span =  models.FloatField(default=0)
    # 封禁时长 min

class defend_log(models.Model):
    """ 攻击日志"""
    ip = models.CharField(max_length=16)
    time = models.DateTimeField(max_length=32)
    type = models.CharField(max_length=32)
    rule = models.CharField(max_length=32)
    # path = models.CharField(max_length=64)
    path = models.CharField(max_length=128)
    address = models.CharField(default="",max_length=32)

class pass_log(models.Model):
    """ 放行日志"""
    ip = models.CharField(max_length=16)
    status = models.CharField(max_length=16)
    time = models.DateTimeField(max_length=32)
    # time = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    # path = models.CharField(max_length=64)
    path = models.CharField(max_length=128)
    post = models.CharField(max_length=128)
    headers = models.CharField(max_length=256)
