import configparser
import datetime
import urllib

import pytz
from django.shortcuts import redirect

import re

from WoofWaf.GeneralConfig.configUtils import getOpenRule, getDefault
from WoofWaf.log.log import logRequest, get_logByIp, get_logByTimeIp
from WoofWaf.models import ip_list, Black_List, defend_log, pass_log
from WoofWaf.waf_utils.getIpInfo import getIp

RCR = "WoofWaf/GeneralConfig/RequestCheckRule.ini"
cc = "WoofWaf/GeneralConfig/cc.ini"


#


def cc_defend(ip):
    # 查看现在启用的规则
    rule = getDefault(cc)['open']
    # 读取所有规则
    config = configparser.ConfigParser()
    config.read(cc)  # 所有规则
    # 获取改规则规定的参数
    if rule == 'default':
        secs = int(getDefault(cc)['timespan'])
        times = int(getDefault(cc)['times'])
    elif (rule in config):
        # 存在rule
        c = config[rule]
        secs = int(c['timespan'])
        times = int(c['times'])
    elif rule == '0':
        return False  # 不限制，直接通过
    else:
        times = 50
        secs = 3
    return limitFrequency(ip, times=times, secs=secs)


def limitFrequency(ip, times=100, secs=10):
    """
    ip
    secs秒
    times次数
    倒数第times次与现在时间小于secs，则过于频繁
    """

    queryset = pass_log.objects.filter(ip=ip)

    if queryset.exists() and queryset.count() > times:
        q = pass_log.objects.filter(ip=ip).order_by('-time')[times:times + 1]
        for a in q:
            t1 = a.time

    else:
        return False
    t2 = datetime.datetime.today()

    t3 = t2.timestamp() - t1.timestamp()
    if t3 < secs:
        return True
        #   频繁
    else:
        #   通过
        return False

#
#
# def limitFrequency(ip,times=60,secs=5):
#     """
#     ip
#     secs秒
#     times次数
#     倒数第times次与现在时间小于secs，则过于频繁
#     """
#     queryset = pass_log.objects.filter(ip=ip)
#
#     if  queryset.exists() and queryset.count()>times:
#         t1=pass_log.objects.filter(ip=ip).order_by('-time')[times:times+1]
#
#     else:
#         return  False
#     t2 = datetime.datetime.today()
#
#     t3 = t2.timestamp()-t1.timestamp()
#     if t3 < secs :
#         return True
#         #   频繁
#     else:
#         #   通过
#         return False
