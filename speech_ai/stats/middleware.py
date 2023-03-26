import time
from datetime import timezone

from django.utils.deprecation import MiddlewareMixin

from stats.models import Visit


class StatsMiddleware(MiddlewareMixin):
    # def __init__(self, get_response):
    #     self.get_response = get_response
    #
    # def __call__(self, request):
    #     start_time = time.time()
    #     response = self.get_response(request)
    #     end_time = time.time()
    #     page_time = end_time - start_time
    #
    #     print(page_time)
    #     # 在此处记录页面停留时间
    #     return response

    def process_request(self, request):

        self.start_time=time.time()


    def process_view(self, request, view_func, *view_args, **view_kwargs):
        # print("--------process_view-----------")
        pass

    def process_response(self, request, response):
        visit = Visit()
        visit.path = request.path
        visit.method = request.method
        visit.status_code = response.status_code
        visit.ip_address = request.META.get('REMOTE_ADDR')
        visit.user_agent = request.META.get('HTTP_USER_AGENT')
        t=(time.time() - self.start_time)*1000 # 毫秒
        if t == 0:
            t = 5
        visit.response_time = self.limit_float_length(t ,4)
        visit.time_stamp=self.start_time


        if request.META.get('CONTENT_LENGTH')=="":
            request_bytes = 0
        else:
            request_bytes = request.META.get('CONTENT_LENGTH')
        # 计算请求和响应的字节数

        response_bytes = len(response.content) if response.content else 0

        visit.bytes_send = response_bytes
        visit.bytes_recv = request_bytes

        visit.save()
        return response



    def limit_float_length(self,num, length):
        # 将浮点数转换为字符串，并指定小数点后的位数
        str_num = '{:.{}f}'.format(num, length)
        # 截取所需的长度
        limited_str = str_num[:length+1]
        # 将字符串转换回浮点数并返回
        return float(limited_str)
