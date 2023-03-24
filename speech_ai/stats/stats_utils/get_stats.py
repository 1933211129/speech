import time

from django.db.models import Avg, Sum

from stats.models import Visit


def ip_nums(t: float = 0, t0=time.time()) -> int:
    """
    时间戳∈[t,t0] 来访ip的数目
    :param t0:默认现在时间
    :param t:
    :return:ip种数
    """
    filtered_objects = Visit.objects.filter(time_stamp__range=(t, t0)).distinct()
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
