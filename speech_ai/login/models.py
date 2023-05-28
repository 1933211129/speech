from django.db import models
import uuid


# 获取压缩成22位的UUID
def uid():
    # return uuid.UUID(str(uuid.uuid4()).replace('-', ''))
    return str(uuid.uuid4()).replace('-', '')


# class Match(models.Model):
#     id = models.CharField(verbose_name=u'赛事ID', max_length=128, primary_key=True, auto_created=True,
#                           default=uid, editable=False)  # 主键
#     organizerID = models.CharField(verbose_name=u'组织者ID', max_length=128, unique=False)  # 主键
#     inf = models.TextField(verbose_name=u'赛事描述')
#

class MyUser(models.Model):
    id = models.CharField(verbose_name=u'用户ID', max_length=128, primary_key=True, auto_created=True,
                          default=uid, editable=False)  # 主键
    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    # temp = (('male', '男'), ('female', '女'))
    registration_time = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(verbose_name='头像', upload_to='avatar', default=u'default.png')

    # 识别身份 0普通用户  1裁判  2管理员
    status_flag = models.CharField(max_length=1, unique=False, default=u'0')

    def __str__(self):
        return f'用户名: {self.username}, 邮箱: {self.email}, 注册时间: {self.registration_time}'

    class Meta:
        ordering = ['registration_time']
        verbose_name = '用户表'


class Pose(models.Model):
    uid = models.CharField(verbose_name=u'用户ID', max_length=128, auto_created=True, editable=False)
    # uid = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='开始日期', default=None)
    img = models.ImageField(verbose_name='图片', max_length=256)
    imgTime = models.CharField(verbose_name='图片时间', default='', max_length=128)
    emotion = models.CharField(verbose_name='表情', max_length=64)
    emotion_prob = models.FloatField(verbose_name='表情置信度', default=0.0)
    pose = models.ImageField(verbose_name='姿态', max_length=256)
    score = models.FloatField(verbose_name='评分', default=-1.0)
    flag = models.BooleanField(verbose_name='是否变化', default=False)
    limbsChanges = models.IntegerField(verbose_name='四肢变化', default=0)
    bodyDeviation = models.IntegerField(verbose_name='人体偏移', default=0)

    def __str__(self):
        return f'时间: {self.date}, 图片时间:{self.imgTime}, 分数: {self.score}, 标志: {self.flag}'


class Speach(models.Model):
    uid = models.CharField(max_length=128, verbose_name=u'用户ID', editable=False, auto_created=True)
    # uid = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date = models.DateTimeField(max_length=20, verbose_name='演讲时间')
    total_score = models.FloatField(max_length=10, verbose_name='总得分')
    content = models.CharField(max_length=10000, verbose_name='内容')
    color_content = models.CharField(max_length=10000, verbose_name='演讲准确度文本', default=None)
    fluency_score = models.FloatField(max_length=10, verbose_name='流畅度')
    integrity_score = models.FloatField(max_length=10, verbose_name='完整度')
    phone_score = models.FloatField(max_length=10, verbose_name='声调')
    tone_score = models.FloatField(max_length=10, verbose_name='音调')
    affix_score = models.FloatField(max_length=10, verbose_name='缀词扣分')
    topic_score = models.FloatField(max_length=10, verbose_name='主旨契合度', null=True, default=None)
    video_path = models.ImageField(verbose_name='视频路径', max_length=256, default=None)

    # 文本情感
    textual_emotion = models.TextField(default=None, null=True)
    # 语音情感
    phonetic_emotion = models.TextField(default=None, null=True)

    def __str__(self):
        return f'时间: {self.date}, 总分: {self.total_score}, 视频路径: {self.video_path}'
