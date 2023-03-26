from stats.stats_utils.get_stats import bytes_send, bytes_recv
from stats.stats_utils.time_transform import strat_of_this_hour


def traffic_recent_hours(n: int) -> list:
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
    recv.append(round(bytes_recv(t=strat_of_this_hour()) / 1024, 2))
    send.append(round(bytes_send(t=strat_of_this_hour()) / 1024, 2))
    return [recv, send]
