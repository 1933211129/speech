from django.db import models


class Table(models.Model):
    speech_time = models.DateTimeField(max_length=20, verbose_name='演讲时间')
    content = models.TextField(max_length=16370, verbose_name='内容')
    fluency_score = models.FloatField(max_length=10, verbose_name='流畅度')
    integrity_score = models.FloatField(max_length=10, verbose_name='完整度')
    phone_score = models.FloatField(max_length=10, verbose_name='声调')
    tone_score = models.FloatField(max_length=10, verbose_name='音调')
    topic_score = models.FloatField(max_length=10, verbose_name='主旨契合度', null=True)
    affix_score = models.FloatField(max_length=10, verbose_name='缀词扣分', null=True)
    total_score = models.FloatField(max_length=10, verbose_name='总得分', null=True)
    body_score = models.FloatField(max_length=10, verbose_name='肢体动作得分', null=True)

#
class text_score(models.Model):
    create_time = models.DateTimeField(primary_key=True, auto_now_add=True)
    text = models.TextField(max_length=16370, verbose_name='内容')
    subject = models.CharField(max_length=20, blank=True)
#
