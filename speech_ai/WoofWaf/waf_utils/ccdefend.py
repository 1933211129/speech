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
#


def cc_check(request):
    """
    :param request: WSGIRequest对象
    """

    # 获取ip地址
    ip=getIp(request)

    # 3.读ip_list表
    queryset = pass_log.objects.filter(ip=ip).first()

    # 4.从表中获取ip状态,
    if queryset is None:
        status = 3
        # 4.1 iplist里没这ip，一会检查的时候如果他要被封就把他记录到ip_list里
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
                redirect("/ParameterError")
                return redirect("/ParameterError")


def limitFrequency(ip,times=60,secs=5):
    """
    ip
    secs秒
    times次数
    倒数第times次与现在时间小于secs，则过于频繁
    """
    queryset = pass_log.objects.filter(ip=ip)

    if  queryset.exists() and queryset.count()>times:
        t1=pass_log.objects.filter(ip=ip).order_by('-time')[times:times+1]

    else:
        return  False
    t2 = datetime.datetime.today()

    t3 = t2.timestamp()-t1.timestamp()
    if t3 < secs :
        return True
        #   频繁
    else:
        #   通过
        return False