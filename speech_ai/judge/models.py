import json

from django.db import models
import uuid


# Create your models here.
def uid():
    return str(uuid.uuid4()).replace('-', '')


# 选手表
class Competitor(models.Model):
    class Meta:
        unique_together = ("race_id", "Cptr_id")

    # 赛事id
    race_id = models.CharField(verbose_name=u'赛事ID', max_length=128, default=uid, editable=False)
    # 选手方面
    # 选手id
    Cptr_id = models.CharField(verbose_name=u'选手ID', max_length=128, default=uid, editable=False)

    # 选手姓名
    Cptr_Name = models.CharField(verbose_name=u'选手姓名', max_length=128)

    # 选手性别
    Cptr_gender = models.CharField(verbose_name=u'性别', max_length=128, default='男')

    # 电话
    Cptr_phone = models.CharField(max_length=11, default=None)

    # 邮箱
    Cptr_email = models.CharField(max_length=50, default=None)

    # 单位
    Cptr_unit = models.CharField(max_length=128, default=None)

    video_upload_date = models.DateTimeField(verbose_name='上传日期', default=None)

    # 视频路径
    video_path = models.FileField(verbose_name=u'视频url', upload_to='judge/video/')

    # 视频所展示图片路径
    img_path = models.ImageField(verbose_name=u'图片url',upload_to='judge/video/picture/', default=None)

    # 人工评分   情感饱和度、肢体动作、演讲逻辑、演讲文采
    HumanScore = models.TextField(default=None, null=True)

    # competitor.PoseScore = json.dumps(lst)
    # lst = json.loads(competitor.PoseScore)

    # 语音评测   流畅度、完整度、声调、音调、缀词分数、契合度
    VoiceScore = models.TextField(default=None, null=True)

    # 姿态评分
    PoseScore = models.TextField(default=None, null=True)

    def __str__(self):
        return f"选手名: {self.Cptr_Name}, 人工打分: {self.HumanScore}, 机器语音打分: {self.VoiceScore}, 机器姿态打分: {self.PoseScore}"

    # 人工评分
    # HumanScore = models.FloatField(verbose_name='人工评分', default=None, null=True)

    # 机器语音评分
    # VoiceScore = models.FloatField(verbose_name='机器语音评分', default=None, null=True)

    # # 流畅度
    # fluency_score = models.FloatField(max_length=10, verbose_name='流畅度')
    #
    # # 完整度
    # integrity_score = models.FloatField(max_length=10, verbose_name='完整度')
    #
    # # 声调
    # phone_score = models.FloatField(max_length=10, verbose_name='声调')
    #
    # # 音调
    # tone_score = models.FloatField(max_length=10, verbose_name='音调')
    #
    # # 缀词分数
    # affix_score = models.FloatField(max_length=10, verbose_name='缀词扣分')
    #
    # # 契合度
    # topic_score = models.FloatField(max_length=10, verbose_name='主旨契合度', null=True, default=None)

    # # 机器姿态评分
    # PoseScore = models.FloatField(verbose_name='机器姿态评分', default=None, null=True)


# 选手参加赛事表
# 【】


# 赛事表
class Race(models.Model):
    # 组织者方面
    # 组织者/申请者id
    OrganizerID = models.CharField(verbose_name=u'组织者ID', max_length=128, unique=False)

    # 组织者/申请者手机
    organizers_mobile = models.CharField(max_length=11)

    # 组织者/申请者邮箱
    organizers_email = models.CharField(max_length=50)

    # 组织者/申请者单位
    organizers_unit = models.CharField(max_length=128)

    # # 组织者/申请者申请原因(例如组织者姓名等)
    # organizers_explain = models.CharField(max_length=256)

    # 赛事方面
    # 申请是否成功
    flag = models.BooleanField(default=False)

    # 赛事id
    race_id = models.CharField(verbose_name=u'赛事ID', max_length=128, primary_key=True, auto_created=True,
                               default=uid, editable=False)
    # 赛题
    race_name = models.CharField(max_length=128, null=False)

    # 赛事时间
    race_time = models.CharField(max_length=128, null=False)

    # 赛事 附件
    # race_file = models.FileField(upload_to='judge/appendix/', blank=True, null=True)
    race_file = models.CharField(max_length=1280, null=False)

    def __str__(self):
        return f'比赛: {self.race_name}, 时间: {self.race_time}, 是否通过: {self.flag} '

    # # 赛事地点
    # race_location = models.CharField(max_length=256)
    #
    # # 赛事其他说明
    # race_content = models.TextField(default=None)
    #
    # # 赛事要求（例如需要身份证等信息）
    # race_required = models.TextField(default=None)
    #
    # # 赛事规则
    # race_rules = models.TextField(default=None)
    #

# 赛事申请表(暂且不用)
# class SpeechContestApplication(models.Model):
#     # 赛事id
#     race_id = models.CharField(verbose_name=u'赛事ID', max_length=128, primary_key=True, auto_created=True,
#                                default=uid, editable=False)
#     # 申请者姓名
#     applicant_name = models.CharField(max_length=30)
#
#     # 申请者手机
#     applicant_mobile = models.CharField(max_length=11)
#
#     # 申请者邮箱
#     applicant_email = models.CharField(max_length=50)
#
#     # 申请者单位
#     organization = models.CharField(max_length=50)
#
#     # 演讲内容
#     speech_content = models.CharField(max_length=4000, blank=True, null=True)
#
#     # 演讲文件
#     speech_file = models.FileField(upload_to='speech_files/', blank=True, null=True)
#
#     # 申请是否成功
#     flag = models.BooleanField(default=False)
