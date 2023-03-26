import datetime
import urllib

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from WoofWaf.GeneralConfig.configUtils import getDefault
from WoofWaf.log.log import get_logByIp, logAll, pass_log, add_pass_log
from WoofWaf.payload_ai.main import payload_predict
from WoofWaf.waf_utils.ccdefend import cc_defend
from WoofWaf.waf_utils.getIpInfo import getIp
from WoofWaf.waf_utils.request_check import request_check, ifTempBlockOK, ifIpBlocked
from WoofWaf.waf_utils.uploadfile_check import check_file

RCR = "WoofWaf/GeneralConfig/RequestCheckRule.ini"
GC = "WoofWaf/GeneralConfig/gc.ini"


class MyTestMiddleware_first(MiddlewareMixin):
    def process_request(self, request):
        # 防止频繁访问
        if cc_defend(getIp(request)):
            return render(request, "WafTemp/frequentlyRequest.html")
        # 检查ip是否放行
        if ifIpBlocked(getIp(request)):
            return render(request, "WafTemp/ip_prohibit.html")
        # 如果开启了Http安全检测：检查请求
        if getDefault(GC)['requestcheck'] == "1":
            # 检查请求
            if request != None:
                a = request_check(request)
                if a:
                    return redirect(reverse('Woof-ParameterError'))

        # if getDefault(GC)['uploadcheck'] == "1":
        #     # 检查上传文件
        #     a = check_file(request)

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        pass

    def process_response(self, request, response):
        # 计入放行日志
        add_pass_log(request, response)
        return response


        # # print("------process_request---------")
        # # Test:输出WSGIRequest对象的属性以学习,test内可删除
        # # 参考网站：https://www.cnblogs.com/limaomao/p/9383799.html
        # # 官网：https://falcon.readthedocs.io/en/stable/api/request_and_response_wsgi.html#
        # # Test start
        # # print("wsgi对象：",type(request))
        # ip = request.META.get('REMOTE_ADDR')
        # # print("ip:" + ip)
        # path = request.path
        # # print("path:" + path)
        # parameter = request.GET
        # # print(type(parameter))
        # realip = request.META.get('access_route')
        # # if realip is None:
        # #     print("real ip == None")
        # # print("url:" + urllib.parse.unquote(request.get_full_path()))
        # # Test end
        #
        # # print(len(get_logByIp(ip)))
        # # print(request.POST)
        #
        # # for parameter in request.POST.values():
        # #     if payload_predict(parameter):
        # #         return render(request,"WafTemp/ParameterError.html")