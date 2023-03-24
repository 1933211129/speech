# 本文件编写于中间件process_request中调用 用来检查request的方法

import datetime
import time
import urllib

import pytz
from django.shortcuts import redirect




import re

from WoofWaf.GeneralConfig.configUtils import getOpenRule, getDefault
from WoofWaf.log.log import logRequest, get_logByIp, get_logByTimeIp
from WoofWaf.models import ip_list, Black_List, defend_log
from WoofWaf.waf_utils.getIpInfo import getIp

RCR = "WoofWaf/GeneralConfig/RequestCheckRule.ini"
#


def request_check(request):
    """
    :param request: WSGIRequest对象
    """
    # 1.获取所有开启的规则
    configList = getOpenRule(RCR)
    # 2.获取ip地址
    ip=getIp(request)

    # 3.读ip_list表
    queryset = ip_list.objects.filter(ip=ip).first()

    # 4.从表中获取ip状态,
    if queryset is None:
        status = 3
        # 4.1 iplist里没这ip，一会检查的时候如果他要被封就把他记录到ip_list里
        # ip = ip_list()
        # ip.ip=getIp(request)
        # ip.status=3
        # ip.save()
    else:
        status = queryset.status
        #  4.2 status : 0 White 1 Black 2 Temp

    # 5. 获取封禁时间
    blockspan = getDefault(RCR)['blockspan']

    # 6.根据打开的规则挨个匹配

    for config in configList:
        # 6.1 检查url
        if config['chkurl']!='0':
            if re.search(config['regex'],urllib.parse.unquote(request.get_full_path())) is not None:
                # 检查出危险攻击
                doRecord(status,request,config,ip,blockspan)
                print('checked')
                return True

        if config['chkpost']!='0':
            for parameter in request.POST.values():
                    if re.search(config['regex'],parameter) is not None:
                        # 检查出危险攻击
                        doRecord(status,request,config,ip,blockspan)

                        print('checked')
                        return True

    return False


def ifBlockIp(ip):
    """
    True 攻击次数触发规则，准备封ip
    """
    queryset = ip_list.objects.filter(ip=ip).first()
    if queryset is not None and queryset.status !=0:
        timespan = int(getDefault(RCR)['timespan'])
        times = int(getDefault(RCR)['times'])
        # 如果timespan时间内的危险请求次数大于times 则加入黑名单 blockspan 分钟
        if(len(get_logByTimeIp(timespan,ip)) > times):
            return True
        else:
            return False


def ifIpBlocked(ip):
    """
    True 封锁，不允许访问
    """
    queryset = ip_list.objects.filter(ip=ip).order_by('id').first()
    # print(queryset.status)
    if queryset is None:
        return False
    elif queryset.status == 0:
        # 白名单
        return False
    elif queryset.status == 1:
        # 黑名单
        return True
    elif queryset.status == 2:
        # 临时黑名单，判断是否到期
        if ifTempBlockOK(ip):
            return False
        else:
            # 封
            return True


def ifTempBlockOK(ip):
    """
    True 解封
    """
    queryset = Black_List.objects.filter(ip=ip).last()
    if queryset is not None:
        span = queryset.prohibit_span
        # 最近的封禁时间
        t1 = queryset.prohibit_time
        # 现在的时间
        t2 = datetime.datetime.today()
        # 已封禁时长，单位 分钟
        t3 = (t2.timestamp()-t1.timestamp())/60
        if t3 > span :
            return True
        else:
            return False
    return True

# 如果违反规则，做此记录
def doRecord(status,request,config,ip,blockspan):

    if status == 1:
        logRequest(request, config, action="WhiteIP")
    else:
        if ifBlockIp(ip):
            if status == 3:
                newIp = ip_list(ip=ip, frequency=1, status=2)
                newIp.save()
            logRequest(request, config, action="Block:" + blockspan)
            # amsterdam_timezone = pytz.timezone('Asia/Shanghai')
            # 写入blacklist表
            # dt = amsterdam_timezone.localize(datetime.datetime.today())
            access = datetime.datetime.today() + datetime.timedelta(minutes=int(blockspan))
            # access_time =datetime.datetime.today() + datetime.timedelta(hours=8) + datetime.timedelta(minutes=int(blockspan))
            newBlockIp = Black_List(prohibit_time=datetime.datetime.today(), prohibit_span=0.15, ip=ip, access_time=access)
            newBlockIp.save()

        else:
            # 不封ip仅记录
            logRequest(request, config, action="unhandled")

    newDefendLog = defend_log(ip=ip, time=datetime.datetime.today(), type=config['type'], rule=config.name,
                              path=request.path,
                              address="中国")
    newDefendLog.save()

