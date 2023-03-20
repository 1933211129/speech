import datetime
import urllib

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.deprecation import MiddlewareMixin

from WoofWaf.GeneralConfig.configUtils import getDefault
from WoofWaf.log.log import get_logByIp, logAll, pass_log, add_pass_log
from WoofWaf.payload_ai.main import payload_predict
from WoofWaf.waf_utils.getIpInfo import getIp
from WoofWaf.waf_utils.request_check import request_check, ifTempBlockOK, ifIpBlocked
from WoofWaf.waf_utils.uploadfile_check import check_file

forbiddenIps = []

RCR = "WoofWaf/GeneralConfig/RequestCheckRule.ini"
GC = "WoofWaf/GeneralConfig/gc.ini"


class MyTestMiddleware_first(MiddlewareMixin):
    def process_request(self, request):

        # print("------process_request---------")
        # Test:输出WSGIRequest对象的属性以学习,test内可删除
        # 参考网站：https://www.cnblogs.com/limaomao/p/9383799.html
        # 官网：https://falcon.readthedocs.io/en/stable/api/request_and_response_wsgi.html#
        # Test start
        # print("wsgi对象：",type(request))
        ip = request.META.get('REMOTE_ADDR')
        # print("ip:" + ip)
        path = request.path
        # print("path:" + path)
        parameter = request.GET
        # print(type(parameter))
        realip = request.META.get('access_route')
        # if realip is None:
        #     print("real ip == None")
        # print("url:" + urllib.parse.unquote(request.get_full_path()))
        # Test end

        # print(len(get_logByIp(ip)))
        # print(request.POST)

        # for parameter in request.POST.values():
        #     if payload_predict(parameter):
        #         return render(request,"WafTemp/ParameterError.html")

        if limitFrequency('127.0.0.1'):
            return render(request, "WafTemp/frequentlyRequest.html")



        if ifIpBlocked(getIp(request)):
            print('block')
            return render(request,"WafTemp/ip_prohibit.html")


        # ifTempBlockOK("127.0.0.1") # 可能为空
        # 如果开启了Http安全检测：
        if getDefault(GC)['requestcheck'] == "1":
            # 检查请求
            if request!=None:
                a = request_check(request)
                return a


        # if getDefault(GC)['ccdefend'] == "1":
        #     # 防止流量攻击
        #     a = cc_check(request)
        #     return a

        if getDefault(GC)['uploadcheck']=="1":
            # 检查上传文件
            a = check_file(request)


        # 通过了安全检测，记入放行日志

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        # print("--------process_view-----------")
        pass

    def process_response(self, request, response):
        add_pass_log(request, response)
        # print("--------process_response()-----")
        return response

def limitFrequency(ip,times=20,secs=5):
    """
    ip
    secs秒
    times次数
    倒数第times次与现在时间小于secs，则过于频繁
    """
    queryset = pass_log.objects.filter(ip=ip)


    if  queryset.exists() and queryset.count()>times:
        q=pass_log.objects.filter(ip=ip).order_by('-time')[times:times + 1]
        for a in q:
            t1= a.time

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




