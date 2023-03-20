from django import forms

from judge.models import Race


class HumanScore(forms.Form):
    # 选手id
    Cptr_id = forms.CharField(label="选手", max_length=128,
                              widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "选手id"}))

    # 情感饱和度、肢体动作、演讲逻辑、演讲文采
    # 情感饱和度
    score1 = forms.FloatField()

    # 肢体动作
    score2 = forms.FloatField()

    # 演讲逻辑
    score3 = forms.FloatField()

    # 演讲文采
    score4 = forms.FloatField()


class VideoForm(forms.Form):
    # 赛事码
    raceID = forms.CharField(label="赛事码", max_length=128,
                             widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "赛事码"}))

    # 姓名
    name = forms.CharField(label="姓名", max_length=128,
                           widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "姓名"}))
    # 性别
    gender = forms.ChoiceField(label="性别", choices=((1, "男"), (2, "女")), initial=1, widget=forms.widgets.Select())

    # 手机号
    phone = forms.CharField(label="手机号", max_length=11,
                            widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "手机号"}))

    # 邮箱
    email = forms.CharField(label="邮箱", max_length=50,
                            widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': "邮箱"}))

    # 单位
    unit = forms.CharField(label="单位", max_length=128,
                           widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "单位"}))

    # 视频
    video = forms.FileField(label="视频", allow_empty_file=False)

    # img = forms.FileField(label="视频图片", allow_empty_file=False)


class RaceForm(forms.Form):
    # 组织者方面
    # 组织者/申请者手机
    organizers_mobile = forms.CharField(label="手机号", max_length=11,
                                        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "手机号"}))

    # 组织者/申请者邮箱
    organizers_email = forms.CharField(label="邮箱", max_length=50,
                                       widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': "邮箱"}))

    # 组织者/申请者单位
    organizers_unit = forms.CharField(label="单位", max_length=128,
                                      widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "单位"}))

    # 组织者/申请者说明(例如组织者姓名等)
    # organizers_explain = forms.CharField(label="组织者说明", max_length=256)

    # 赛事方面
    # 赛题
    race_name = forms.CharField(label="赛题", max_length=128,
                                widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "赛题"}))
    # 赛事时间
    race_time = forms.CharField(label="时间", widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "时间"}))

    # 赛事 附件
    # race_file = forms.FileField(label="附件")
    race_file = forms.CharField(label="赛事介绍")

    # # 赛事地点
    # race_location = forms.CharField(label="地点", max_length=256,
    #                                 widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "地点"}))
    # # 赛事其他说明
    # race_content = forms.CharField(label="说明", widget=forms.TextInput(attrs={'class': 'textarea', 'placeholder': "说明"}))
    #
    # # 赛事要求（例如需要身份证等信息）
    # race_required = forms.CharField(label="要求",
    #                                 widget=forms.TextInput(attrs={'class': 'textarea', 'placeholder': "要求"}))
    #
    # # 赛事规则
    # race_rules = forms.CharField(label="规则",
    #                              widget=forms.TextInput(attrs={'class': 'textarea', 'placeholder': "规则"}))

    # race_id
    # OrganizerID
    # flag # 申请是否成功
