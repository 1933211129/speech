import time

from stats.stats_utils.get_stats import bytes_send, bytes_recv, request_nums
from stats.stats_utils.time_transform import strat_of_this_hour, today_zero_clock


def traffic_recent_hours(n: int, ttt=time.time()) -> list:
    """
    n-1小时之前至今每小时的进出流量列表,共n条
    :param n:
    :return:KB
    """
    recv = []
    send = []
    t0 = strat_of_this_hour()
    t = t0 - 3600 * n
    while (n != 1):
        # r = bytes_recv(t=t, t0=t + 3600, ip="*", path="*")
        # s = bytes_send(t=t, t0=t + 3600, ip="*", path="*")
        r = round(bytes_recv(t=t, t0=t + 3600, ip="*", path="*") / 1024, 2)
        s = round(bytes_send(t=t, t0=t + 3600, ip="*", path="*") / 1024, 2)
        t = t + 3600
        recv.append(r)
        send.append(s)
        n = n - 1
    # recv.append(bytes_recv(t=strat_of_this_hour()))
    # send.append(bytes_send(t=strat_of_this_hour()))
    recv.append(round(bytes_recv(t=strat_of_this_hour(), t0=ttt) / 1024, 2))
    send.append(round(bytes_send(t=strat_of_this_hour(), t0=ttt) / 1024, 2))
    return [recv, send]


def request_num_for_day(n: int, ttt=time.time()) -> list:
    list = []
    t = today_zero_clock() - 24 * 3600 * n

    while (n != 1):
        num=request_nums(t=t, t0=t+24*3600)
        t = t + 24 * 3600
        list.append(num)
        n = n - 1
    list.append(request_nums(t=today_zero_clock(), t0=ttt))
    return list
