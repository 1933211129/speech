from datetime import datetime, timedelta

from WoofWaf.models import Black_List, defend_log


def get_attack_times():
    """
    24h内defend_log条数
    :return:
    """
    # 获取当前时间
    now = datetime.now()

    # 计算24小时前的时间
    delta = timedelta(hours=24)
    before_24h = now - delta

    # 查询prohibit_time字段在24小时之内的记录
    result = defend_log.objects.filter(time__gte=before_24h, time__lte=now)

    return result.count()


def get_ip_block_times():
    """
    24内ip封禁记录条数
    :return:
    """
    # 获取当前时间
    now = datetime.now()

    # 计算24小时前的时间
    delta = timedelta(hours=24)
    before_24h = now - delta

    # 查询prohibit_time字段在24小时之内的记录
    result = Black_List.objects.filter(prohibit_time__gte=before_24h, prohibit_time__lte=now)

    return result.count()
