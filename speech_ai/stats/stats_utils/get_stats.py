import time
from statistics import median

from django.db.models import Avg, Sum, Count, Max, Min

from stats.models import Visit


def ip_nums(t: float = 0, t0=time.time()) -> int:
    """
    时间戳∈[t,t0] 来访ip的数目,种数，种数，种数，种数
    :param t0:默认现在时间
    :param t:
    :return:ip种数
    """
    filtered_objects = Visit.objects.filter(time_stamp__range=(t, t0)).values('ip_address').distinct()
    return filtered_objects.count()


def request_nums(t: float = 0, t0=time.time()) -> int:
    """
    时间戳∈[t,t0] 请求的数量
    :param t0:默认现在时间
    :param t:
    :return:
    """
    filtered_objects = Visit.objects.filter(time_stamp__range=(t, t0))
    return filtered_objects.count()


def method_stats(t: float = 0, t0=time.time()) -> dict:
    """
    时间戳∈[t,t0] get和post请求数
    :param t0:
    :param t:
    :return:
    'POST': post_num,数量
    'GET': get_num,
    'total':total,总数
    'get':get_pct,[0~100] 百分比整数部分
    'post':post_pct
    """

    get_num = Visit.objects.filter(time_stamp__range=(t, t0), method="GET").count()
    post_num = Visit.objects.filter(time_stamp__range=(t, t0), method="POST").count()
    total = get_num + post_num
    if get_num == 0:
        get_pct = 0
    else:
        get_pct = int((get_num / total) * 100)
    post_pct = 100 - get_pct
    if post_num == 0:
        post_pct = 0
    method_num_dict = {'POST': post_num, 'GET': get_num, 'total': total, 'get': get_pct, 'post': post_pct}
    return method_num_dict


def ip_url_times(t: float = 0, path: str = "*", ip: str = "*", t0=time.time()) -> int:
    """
    时间戳∈[t,t0] ip 对 path 的访问量
    :param t0:
    :param t:
    :param ip:
    :param path:
    :return:int访问量
    """

    if ip == "*":
        if path == "*":
            # t秒前至今 本站收到的访问数
            filtered_objects = Visit.objects.filter(time_stamp__range=(t, t0))
        else:
            # t至今 path 访问数
            filtered_objects = Visit.objects.filter(time_stamp__range=(t, t0), path=path)
    else:
        if path == "*":
            # t秒前至今 某ip的访问数
            filtered_objects = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip)
        else:
            # t至今 某ip对path的访问数
            filtered_objects = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip, path=path)

    return filtered_objects.count()


def url_average_response_time(t: float = 0, path: str = "*", t0=time.time()) -> float:
    """
    时间戳∈[t,t0] path 的平均响应时间
    :param t0:
    :param t:
    :param path:
    :return:毫秒
    """

    if path == "*":
        # all
        average_value = Visit.objects.filter(time_stamp__range=(t, t0)).aggregate(Avg('response_time'))[
            'response_time__avg']
    else:
        # just path
        average_value = Visit.objects.filter(time_stamp__range=(t, t0), path=path).aggregate(Avg('response_time'))[
            'response_time__avg']

    return average_value


def bytes_send(t: float = 0, path: str = "*", ip: str = "*", t0=time.time()) -> float:
    """
    时间戳∈[t,t0] path 向 ip 发送的流量：网站发送的流量
    :param t0:
    :param ip:
    :param t:
    :param path:
    :return: 字节bytes
    """

    if ip == "*":
        if path == "*":
            send_sum = Visit.objects.filter(time_stamp__range=(t, t0)).aggregate(Sum('bytes_send'))['bytes_send__sum']
        else:
            send_sum = Visit.objects.filter(time_stamp__range=(t, t0), path=path).aggregate(Sum('bytes_send'))[
                'bytes_send__sum']
    else:
        if path == "*":
            send_sum = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip).aggregate(Sum('bytes_send'))[
                'bytes_send__sum']
        else:
            send_sum = \
                Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip, path=path).aggregate(Sum('bytes_send'))[
                    'bytes_send__sum']
    if send_sum is None:
        send_sum = 0
    return send_sum


def bytes_recv(t: float = 0, path: str = "*", ip: str = "*", t0=time.time()) -> float:
    """
    时间戳∈[t,t0] ip 对 path 发送的流量：用户发送的流量 ，网站接收的流量
    :param t0:
    :param ip:
    :param t:
    :param path:
    :return:
    """
    if ip == "*":
        if path == "*":
            recv_sum = Visit.objects.filter(time_stamp__range=(t, t0)).aggregate(Sum('bytes_recv'))['bytes_recv__sum']
        else:
            recv_sum = Visit.objects.filter(time_stamp__range=(t, t0), path=path).aggregate(Sum('bytes_recv'))[
                'bytes_recv__sum']
    else:
        if path == "*":
            recv_sum = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip).aggregate(Sum('bytes_recv'))[
                'bytes_recv__sum']
        else:
            recv_sum = \
                Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip, path=path).aggregate(Sum('bytes_recv'))[
                    'bytes_recv__sum']
    if recv_sum is None:
        recv_sum = 0
    return recv_sum

# 写到这里发现每次都分四个叉,十分地冗余,之前没想到先如何封装四个叉,现在补上
def ip_path_queryset(t: float = 0, path: str = "*", ip: str = "*", t0=time.time()):
    """
    返回一组查询罢了，然后尽情地统计数据吧～
    :param t:
    :param path:
    :param ip:
    :param t0:
    :return:
    """
    if ip == "*":
        if path == "*":
            queryset = Visit.objects.filter(time_stamp__range=(t, t0))
        else:
            queryset = Visit.objects.filter(time_stamp__range=(t, t0), path=path)
    else:
        if path == "*":
            queryset = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip)
        else:
            queryset = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip, path=path)

    return queryset


def rsp_time(t: float = 0, path: str = "*", ip: str = "*", t0=time.time()) -> list:
    # 依次为响应速度的最小值、最大值、中位数、平均值
    # 定义 1000/响应时间(ms) 为响应速度 条/秒
    my_queryset = ip_path_queryset(t=t,path=path,ip=ip,t0=t0)
    rsp_time_list = []
    if my_queryset is not None:

        max_response_time = my_queryset.aggregate(max_response_time=Max('response_time'))['max_response_time']
        min_response_time = my_queryset.aggregate(min_response_time=Min('response_time'))['min_response_time']
        avg_response_time = my_queryset.aggregate(avg_response_time=Avg('response_time'))['avg_response_time']
        # 计算中位数
        response_times = my_queryset.values_list('response_time', flat=True)
        median_response_time = median(response_times)
        if max_response_time*min_response_time*avg_response_time*median_response_time !=0:
            rsp_time_list.extend([1000/max_response_time,min(1000/min_response_time,249.2),1000/median_response_time,1000/avg_response_time])
        else:
            rsp_time_list = [0, 0, 0, 0]
    else:
        rsp_time_list = [0,0,0,0]
    return rsp_time_list


def status_code(t: float = 0, path: str = "*", ip: str = "*", t0=time.time()):
    """
    时间戳∈[t,t0] ip 对 path 的访问中，状态码及其对应数量的字典
    :param t0:
    :param ip:
    :param t:
    :param path:
    :return:
    """
    if ip == "*":
        if path == "*":

            result = Visit.objects.filter(time_stamp__range=(t, t0)).values('status_code').annotate(total=Count('status_code')).order_by('status_code')

        else:
            # 指定path

            result = Visit.objects.filter(time_stamp__range=(t, t0), path=path).values('status_code').annotate(
                total=Count('status_code')).order_by('status_code')

    else:
        # 指定ip
        if path == "*":
            result = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip).values('status_code').annotate(
                total=Count('status_code')).order_by('status_code')

        else:
            result = Visit.objects.filter(time_stamp__range=(t, t0), ip_address=ip, path=path).values(
                'status_code').annotate(total=Count('status_code')).order_by('status_code')

    return result
