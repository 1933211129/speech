# 要查上个月的数据，应该查t秒前的数据，求t
import time
from datetime import timedelta
import datetime

def today_zero_clock() -> float:
    """
    今天00:00的时间戳(昨天24:00)
    :return:
    """
    today = datetime.datetime.today()  # 获取当前日期时间
    midnight = datetime.datetime.combine(today, datetime.datetime.min.time())  # 将时间设置为 00:00
    timestamp = int(midnight.timestamp())  # 转换为 Unix 时间戳

    return timestamp


def nday_zero_clock(n: int) -> float:
    """
    n天前00:00的时间戳,n=0时为今早00:0:0
    :return:
    """
    today = datetime.today()  # 获取当前日期时间
    midnight = datetime.combine(today, datetime.min.time())  # 将时间设置为 00:00
    timestamp = int(midnight.timestamp())  # 转换为 Unix 时间戳

    return timestamp - n * 86400


def day_before(n: int) -> float:
    """
    n天前00:00的时间戳
    :param n:
    :return:
    """
    today = datetime.today()  # 获取当前日期时间
    midnight = (today - timedelta(days=n)).replace(hour=0, minute=0, second=0, microsecond=0)  # n 天前凌晨 00:00
    timestamp = int(midnight.timestamp())  # 转换为 Unix 时间戳
    return timestamp


def first_day_of_month(n: int) -> float:
    """
    计算n个月前当月第一天00:00的时间戳
    :param n:
    :return:
    """
    today = datetime.today()  # 获取当前日期时间
    while True:
        if n > 0 and n < 12:
            if today.month - n <= 0:
                n = n - today.month
                today = today.replace(year=today.year - 1, month=12 - n, day=1)
                midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)  # 设置为 00:00
                timestamp = midnight.timestamp()  # 转换为 Unix 时间戳
                return timestamp
            else:
                today = today.replace(month=today.month - n, day=1)
                midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)  # 设置为 00:00
                timestamp = midnight.timestamp()  # 转换为 Unix 时间戳
                return timestamp
        elif n == 0:
            today = today.replace(day=1)
            midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)  # 设置为 00:00
            timestamp = midnight.timestamp()  # 转换为 Unix 时间戳
            return timestamp

        elif n >= 12:
            y = int(n / 12)
            today = today.replace(year=today.year - y, day=1)
            # 减去一年
            n = n - 12 * y
        else:
            return 0


def nDay_ago_str(n: int):
    """
    n天前的日期
    :param n:
    :return:
    """
    past_date = datetime.date.today() - datetime.timedelta(days=n)
    return past_date.strftime('%m-%d')


def ago_day_list(n: int) -> list:
    """
    n-1天前至今的日期（一共n天），今天03-23
    :param n:
    :return: ['03-17', '03-18', '03-19', '03-20', '03-21', '03-22', '03-23']
    """
    list = []
    n=n-1
    while (n != -1):
        list.append(nDay_ago_str(n))
        n = n - 1
    return list


def hour_list(n) -> list:
    """
    n-1小时前至今的时间列表（一共n条），现在20:09
    :param n:取12
    :return:['9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00']
    """
    list = []
    now = datetime.datetime.now()
    list.append(str(now.hour) + ":00")
    while (n != 1):
        one_hour_ago = now - datetime.timedelta(hours=1)
        list.append(str(one_hour_ago.hour) + ":00")
        now = one_hour_ago
        n = n - 1
    list.reverse()
    return list


def strat_of_this_hour() -> float:
    """
    本小时初的时间戳
    这里不将start设置为参数可能会导致这个时间是项目启动时的时间，还没来及测试
    :return:
    """
    today = datetime.datetime.today()
    start = today.replace(minute=0, second=0, microsecond=0)
    return start.timestamp()




if __name__ == "__main__":
    print(-((day_before(1) - time.time()) / 3600) - 24)
