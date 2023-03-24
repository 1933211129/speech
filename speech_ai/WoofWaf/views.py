from django.shortcuts import render
import requests
from django.shortcuts import render, redirect, HttpResponse
from gevent import time
from WoofWaf import models
from WoofWaf.GeneralConfig.configUtils import swtichStatus, getAllRule, delConfig, getDefault, setField
from WoofWaf.GeneralConfig.httpconfig import addRequestCheckRule, setRequestCheckRule

from WoofWaf.log.log import get_all_log, get_logByIp, atklog
from WoofWaf.models import Black_List, ip_list
from WoofWaf.waf_utils.get_defend_log import get_defend_log, get_pass_log
from stats.stats_utils.get_stats import method_stats, bytes_recv, bytes_send
from stats.stats_utils.time_stats import traffic_recent_hours
from stats.stats_utils.time_transform import hour_list, strat_of_this_hour

RCR = "WoofWaf/GeneralConfig/RequestCheckRule.ini"
GC = "WoofWaf/GeneralConfig/gc.ini"


# Create your views here.

def secure_login(request):
    return render(request, "WafTemp/login.html")


def secure_index(request):
    # 请求方法饼状图
    # 七天内数据
    method = method_stats(t=time.time() - (7 * 24 * 3600))
    data_pie = [
        {'name': 'get', 'value': method['get']},
        {'name': 'post', 'value': method['post']},
    ]

    # 12h流量趋势：双折线图
    traffic = traffic_recent_hours(12)
    # 12h时间表
    hourList = hour_list(12)

    # 攻击次数、IP封禁、ip总数、请求次数、总流量、进、出
    attack_num = 18
    ip_block_num=2
    ip_num=34
    request_num=89
    recv = bytes_recv(t=strat_of_this_hour() - 24 * 3600)
    send = bytes_send(t=strat_of_this_hour() - 24 * 3600)
    total_traffic = recv + send
    row = [attack_num,ip_block_num,ip_num,request_num, total_traffic, recv, send]

    return render(request, "WafTemp/index.html", {'data_pie': data_pie,
                                                  'row': row
                                                  })


def secure_ip_list(request):
    queryset = ip_list.objects.all()
    return render(request, "WafTemp/ip_list.html", {'queryset': queryset})


def update_ip_list(request):
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
    queryset = Black_List.objects.all()
    return render(request, "WafTemp/temp_black_list.html", {'queryset': queryset})


def httpCheck(request):
    if request.method == "GET":
        configlist = getAllRule(RCR)
        return render(request, "WafTemp/HttpCheck.html", {'configlist': configlist})


def httpCheckAddRule(request):
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


# ip封禁配置
def httpCheckSetIpBlock(request):
    if request.method == "POST":
        blockspan = request.POST.get(key="blockspan", default="15")
        times = request.POST.get(key="times", default="5")
        timespan = request.POST.get(key="timespan", default="1")
        if timespan == "": timespan = "1"
        if blockspan == "": blockspan = "15"
        if times == "": times = "5"

        import re
        if not bool(re.match("^[0-9]*$", blockspan + times + timespan)):
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
    return render(request, "WafTemp/CCDefend.html")


def settings(request):
    gc = getDefault(GC)
    rcr = getDefault(RCR)
    return render(request, "WafTemp/settings.html", {'gc': gc, 'rcr': rcr})


def secure_defend_log(request):
    queryset = get_defend_log()
    return render(request, "WafTemp/defend_log.html", {'queryset': queryset, })


def secure_trace_log(request):
    loglist = get_all_log()

    return render(request, "WafTemp/trace_log.html", {'loglist': loglist, })


def secure_pass_log(request):
    queryset = get_pass_log()

    return render(request, "WafTemp/pass_log.html", {'queryset': queryset, })


def ParameterError(request):
    return render(request, "WafTemp/ParameterError.html")
