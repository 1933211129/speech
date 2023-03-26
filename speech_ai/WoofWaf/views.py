from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render
import requests
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from gevent import time
from WoofWaf import models
from WoofWaf.GeneralConfig.configUtils import swtichStatus, getAllRule, delConfig, getDefault, setField
from WoofWaf.GeneralConfig.httpconfig import addRequestCheckRule, setRequestCheckRule

from WoofWaf.log.log import get_all_log, get_logByIp, atklog
from WoofWaf.models import Black_List, ip_list, WafUserManager, waf_admin
from WoofWaf.waf_utils.get_data import get_attack_times, get_ip_block_times
from WoofWaf.waf_utils.get_defend_log import get_defend_log, get_pass_log
from stats.stats_utils.get_stats import method_stats, bytes_recv, bytes_send, status_code, rsp_time, ip_nums, \
    request_nums
from stats.stats_utils.time_stats import traffic_recent_hours
from stats.stats_utils.time_transform import hour_list, strat_of_this_hour
from django.contrib.auth import logout

RCR = "WoofWaf/GeneralConfig/RequestCheckRule.ini"
GC = "WoofWaf/GeneralConfig/gc.ini"
cc = "WoofWaf/GeneralConfig/cc.ini"


# Create your views here.
def login_waf(request):
    if request.user.is_authenticated:
        # 若已经登陆，跳转index
        return redirect(reverse('WoofWaf-views-index'))
    # 重定向来的未登录用户
    if request.method == 'GET' and request.META.get('HTTP_REFERER'):
        return render(request, 'WafTemp/login.html', {'rdct': True})
    # 登录判断
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('WoofWaf-views-index'))
        else:
            # 登录验证失败
            return render(request, 'WafTemp/login.html', {'error': '用户名或密码错误'})
    # 暂时没用好像？
    elif request.method == 'GET' and request.GET.get(key='logout') == 'True':
        logout(request)
        return redirect('/waf/login?logout=False')

    else:
        return render(request, 'WafTemp/login.html')

def logout_waf(request):
    logout(request)
    return redirect(reverse('WoofWaf-views-login'))



# def secure_login(request):
#     return render(request, "WafTemp/login.html")


def secure_index(request):

    # wa = get_user_model()
    # admin=wa.objects.create_user(username="admin",password="admin")
    # admin.save()
    import datetime
    import random
    # wa = get_user_model()
    # admin = wa.objects.create_user(username="admin", password="admin")
    # admin.save()
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    # 请求方法饼状图
    # 七天内数据
    response_status = status_code(t=strat_of_this_hour() - 24 * 3600,t0=time.time())
    # 将产生的response_status改为列表类型
    data_list = list(response_status.values('status_code', 'total'))
    # 将data_list列表改为可直接绘制饼图的格式
    pie2_result_list = [{'name': data['status_code'], 'value': data['total']} for data in data_list]
    # print(result_list)
    method = method_stats(t=time.time() - (7 * 24 * 3600),t0=time.time())
    data_pie = [
        {'name': 'get', 'value': method['GET']},
        {'name': 'post', 'value': method['POST']},
    ]
    # print(data_pie)

    # 12h流量趋势：双折线图数据，二维列表形式
    traffic = traffic_recent_hours(18)
    # 12h时间表，x轴
    hourList = hour_list(18)

    # print(traffic)
    # 攻击次数、IP封禁、ip总数、请求次数、总流量、进、出
    attack_num = get_attack_times()
    ip_block_num = get_ip_block_times()
    ip_num = ip_nums(t=strat_of_this_hour() - 24 * 3600,t0=time.time())
    request_num = request_nums(t=strat_of_this_hour() - 24 * 3600,t0=time.time())
    recv = bytes_recv(t=strat_of_this_hour() - 24 * 3600,t0=time.time())
    send = bytes_send(t=strat_of_this_hour() - 24 * 3600,t0=time.time())
    total_traffic = recv + send
    row = [attack_num, ip_block_num, ip_num, request_num, total_traffic, recv, send]

    # 获取最近七天内日期作为第二个折线图的横坐标
    today = datetime.date.today()
    dates = [str((today - datetime.timedelta(days=i)).strftime('%m-%d')) for i in range(6, -1, -1)]  # 获取到时间列表
    # 生成随机整数
    two_line_data = [random.randint(7, 18) for _ in range(7)]

    return render(request, "WafTemp/index.html", {'data_pie': data_pie,  # 第一个饼图数据
                                                  'row': row,
                                                  'response_status': pie2_result_list,  # 第二个饼图数据
                                                  'data_line': traffic,  # 第一个折线图的数据
                                                  'data_line_xaxis': hourList,  # 第一个折线图的横坐标
                                                  'day_7': dates,  # 第二个折线图的横坐标
                                                  'two_line_data': two_line_data,  # 第二个折线图的数据
                                                  })


def secure_ip_list(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    queryset = ip_list.objects.all()

    return render(request, "WafTemp/ip_list.html", {'queryset': queryset})


def update_ip_list(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "POST":
        ip = request.POST.get(key="ip", default="")
        status = int(request.POST.get(key="status", default=""))
        dcp = request.POST.get(key="dcp", default="")
        if (ip != "") and (status != ""):
            try:
                row = ip_list.objects.get(ip=ip)
                row.status = status
                row.description = dcp
                row.save()
                return HttpResponse("修改成功")
            except:
                return HttpResponse("修改失败")


def add_ip_list(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "POST":
        ip = request.POST.get(key="ip", default="")
        status = int(request.POST.get(key="status", default="0"))
        dcp = request.POST.get(key="dcp", default="无")
        import re
        # 正则表达式
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        # 匹配
        match = re.match(ipv4_pattern, ip)
        # 输出结果
        if match:
            if (ip != "") and (status != ""):
                try:
                    newIp = ip_list(ip=ip, status=status, description=dcp)
                    newIp.save()
                    return HttpResponse("添加成功")
                except:
                    return HttpResponse("添加失败")
        else:
            return HttpResponse("添加失败,IP地址不合法")


def secure_temp_black_list(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    queryset = Black_List.objects.all()
    return render(request, "WafTemp/temp_black_list.html", {'queryset': queryset})


def httpCheck(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "GET":
        configlist = getAllRule(RCR)
        return render(request, "WafTemp/HttpCheck.html", {'configlist': configlist})


def httpCheckAddRule(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "POST":
        ruleName = request.POST.get(key="ruleName", default="")
        regex = request.POST.get(key="re", default="")
        u = request.POST.get(key="u", default="")
        cookie = request.POST.get(key="cookie", default="")
        p = request.POST.get(key="p", default="")
        h = request.POST.get(key="h", default="")
        dcp = request.POST.get(key="dcp", default="无")
        type = request.POST.get(key="type", default="未确定")
        if dcp == "" or dcp == "undefined":
            dcp = "无"
        if type == "" or type == "undefined":
            type = "未确定"
        if ruleName == "undefined":
            return HttpResponse("规则名不能为空")
        import re
        if not bool(re.match("^[A-Za-z0-9_]*$", ruleName)):
            return HttpResponse("规则名只允许数字、字母、下划线的组合")
        if regex == "undefined" or regex == "":
            return HttpResponse("正则不能为空")

        a = addRequestCheckRule(ruleName, regex.replace("%2B", "+"), u, cookie, p, h, dcp.replace("%2B", "+"),
                                type.replace("%2B", "+"), Satus="1")
        if a == 0:
            return HttpResponse("添加成功")
        elif a == 1:
            return HttpResponse("已存在此规则，请重命名")
        elif a == 2:
            return HttpResponse("规则中请勿包含'#'，'；'")
        else:
            return HttpResponse("添加失败")


def httpCheckDelRule(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "POST":
        ruleName = request.POST.get(key="ruleName", default="")
        a = delConfig(RCR, ruleName)
        if a == 0:
            return HttpResponse("删除成功")
        elif a == 1:
            return HttpResponse("规则不存在")
        else:
            return HttpResponse("删除失败")


def httpCheckSetRule(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "POST":
        ruleName = request.POST.get(key="ruleName", default="")
        new_Name = request.POST.get(key="newName", default="")
        regex = request.POST.get(key="re", default="")
        u = request.POST.get(key="u", default="")
        cookie = request.POST.get(key="cookie", default="")
        p = request.POST.get(key="p", default="")
        h = request.POST.get(key="h", default="")
        dcp = request.POST.get(key="dcp", default="无")
        type = request.POST.get(key="type", default="未确定")

        if dcp == "" or dcp == "undefined":
            dcp = "无"
        if type == "" or type == "undefined":
            type = "未确定"
        if new_Name == "undefined" or new_Name == "":
            return HttpResponse("规则名不能为空")
        import re
        if not bool(re.match("^[A-Za-z0-9_]*$", new_Name)):
            return HttpResponse("规则名只允许数字、字母、下划线的组合")
        if ruleName == "undefined" or ruleName == "":
            return HttpResponse("此规则不存在")
        if regex == "undefined" or regex == "":
            return HttpResponse("正则不能为空")

        a = setRequestCheckRule(ruleName, new_Name, regex.replace("%2B", "+"), u, cookie, p, h, dcp.replace("%2B", "+"),
                                type.replace("%2B", "+"), Satus="1")
        if a == 0:
            return HttpResponse("修改成功")
        elif a == 1:
            return HttpResponse("规则不存在")
        elif a == 2:
            return HttpResponse("规则中请勿包含'#'，'；'")
        else:
            return HttpResponse("修改失败")


# 规则开关
def httpCheckSwitch(request, ):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "GET":
        switchSection = request.GET.get(key="switchSection", default="")
        config = request.GET.get(key="config", default="")
        if switchSection != "" and config != "":
            try:
                if config == "RCR":
                    swtichStatus(RCR, switchSection, "status")
                elif config == "GC":
                    swtichStatus(GC, "DEFAULT", switchSection)
                return HttpResponse("修改成功")
            except:
                return HttpResponse("修改失败")


# 规则开关
def ccSwitch(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))

    if request.method == "GET":
        rule = request.GET.get(key="rule", default="default")
        try:
            setField(cc, 'DEFAULT', 'open', rule)
            return HttpResponse("修改成功")
            print(111)
        except:
            print(0)
            return HttpResponse("修改失败")
        # if switchSection != "" and config != "":
        #     try:
        #         if config == "RCR":
        #             swtichStatus(RCR, switchSection, "status")
        #         elif config == "GC":
        #             swtichStatus(GC, "DEFAULT", switchSection)
        #         return HttpResponse("修改成功")
        #     except:
        #         return HttpResponse("修改失败")


# ip封禁配置
def httpCheckSetIpBlock(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    if request.method == "POST":
        blockspan = request.POST.get(key="blockspan", default="15")
        times = request.POST.get(key="times", default="5")
        timespan = request.POST.get(key="timespan", default="1")
        if timespan == "": timespan = "1"
        if blockspan == "": blockspan = "15"
        if times == "": times = "5"

        import re
        BOOL = bool(re.match("^\d+$", blockspan) and re.match("^[0-9]*$", times) and re.match("^[0-9]*$", timespan))

        if BOOL != True :

            return HttpResponse("请仅输入数字")

        try:

            setField(RCR, 'DEFAULT', 'blockspan', blockspan)
            setField(RCR, 'DEFAULT', 'times', times)
            setField(RCR, 'DEFAULT', 'timespan', timespan)
            return HttpResponse("修改成功")

        except:
            return HttpResponse("修改失败")



def uploadDefend(request):
    return render(request, "WafTemp/UploadDefend.html")


def CCDefend(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    rule = getDefault(cc)['open']
    # 3day 条/秒 list 最小值、最大值、中位数、平均值
    rsp_speed = rsp_time(t=time.time() - (3 * 24 * 3600))  # 毫秒

    return render(request, "WafTemp/CCDefend.html",{'openrule':rule})


def settings(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    gc = getDefault(GC)
    rcr = getDefault(RCR)
    rule = getDefault(cc)['open']
    return render(request, "WafTemp/settings.html", {'gc': gc, 'rcr': rcr,'openrule':rule})


def secure_defend_log(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    queryset = get_defend_log()
    return render(request, "WafTemp/defend_log.html", {'queryset': queryset, })


def secure_trace_log(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    loglist = get_all_log()

    return render(request, "WafTemp/trace_log.html", {'loglist': loglist, })


def secure_pass_log(request):
    if not request.user.is_authenticated:
        return redirect(reverse('WoofWaf-views-login'))
    queryset = get_pass_log()

    return render(request, "WafTemp/pass_log.html", {'queryset': queryset, })


def ParameterError(request):

    return render(request, "WafTemp/ParameterError.html")
