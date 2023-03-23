# 要查上个月的数据，应该查t秒前的数据，求t
import time
from datetime import datetime, timedelta


def today_zero_clock() -> float:
    """
    今天00:00的时间戳(昨天24:00)
    :return:
    """
    today = datetime.today()  # 获取当前日期时间
    midnight = datetime.combine(today, datetime.min.time())  # 将时间设置为 00:00
    timestamp = int(midnight.timestamp())  # 转换为 Unix 时间戳

    return timestamp

def day_before(n:int)->float:
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
                timestamp = midnight.timestamp() # 转换为 Unix 时间戳
                return timestamp
            else:
                today = today.replace(month=today.month - n, day=1)
                midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)  # 设置为 00:00
                timestamp = midnight.timestamp()  # 转换为 Unix 时间戳
                return timestamp
        elif n ==0 :
            today = today.replace( day=1)
            midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)  # 设置为 00:00
            timestamp = midnight.timestamp()  # 转换为 Unix 时间戳
            return timestamp

        elif n >= 12:
            y = int(n / 12)
            today = today.replace(year=today.year - y, day=1)
            # 减去一年
            n = n - 12*y
        else:
            return 0


if __name__ == "__main__":
    print(-((day_before(1)-time.time())/3600)-24)
