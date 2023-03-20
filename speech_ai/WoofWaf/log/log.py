import json
import logging
import re
import urllib

import pytz

from WoofWaf.models import pass_log
from WoofWaf.waf_utils.getIpInfo import getIp

AR = "WoofWaf/log/AttackRequest.log"
logger = logging.getLogger(__name__)
# getLogger() 返回对具有指定名称的记录器实例的引用（如果已提供），或者如果没有则返回 root 。

logger.setLevel(logging.INFO)
# Logger.setLevel() 指定记录器将处理的最低严重性日志消息，其中 debug 是最低内置严重性级别， critical 是最高内置严重性级别。
# 例如，如果严重性级别为 INFO ，则记录器将仅处理 INFO 、 WARNING 、 ERROR 和 CRITICAL 消息，并将忽略 DEBUG 消息。

formatter = logging.Formatter('%(asctime)s:%(message)s:')

# 用于将日志输出到文件中
file_handler = logging.FileHandler(AR)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


# Logger.addHandler() 和 Logger.removeHandler() 从记录器对象中添加和删除处理器对象。
class atklog:
    date = ""
    time = ""
    ip = ""
    type = ""
    rulename = ""
    action = ""
    method = ""
    path = ""
    full_path = ""
    headers = ""
    file = ""

    # 定义构造方法
    def __init__(self, date, time, ip, type, rulename, action, method, path, full_path, headers, id="0", file=None,
                 post=None):
        self.date = date
        self.time = time
        self.datetime = datetime.datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S,%f")
        self.ip = ip
        self.type = type
        self.rulename = rulename
        self.action = action
        self.method = method
        self.path = path
        self.full_path = full_path
        self.headers = headers
        self.headerdict = eval(headers)
        self.file = file
        self.post = post
        self.id = id

    # 输入一行日志来创建atklog, log=atklog.get_ByLine(line)
    # 资料：https://blog.csdn.net/weixin_48580001/article/details/115220956
    @classmethod
    def getByLine(cls, line):
        # 这里第一个参数是cls， 表示调用当前的类名
        obj = re.compile(r'^(?P<date>\d{4}-\d{2}-\d{2})\s'
                         r'(?P<time>\d{2}:\d{2}:\d{2},\d{3}):'
                         r'(?P<ip>.*?)\|'
                         r'(?P<type>.*?)-'
                         r'(?P<rulename>.*?)\|'
                         r'(?P<action>.*?)\|'
                         r'(?P<method>.*?)\|'
                         r'(?P<path>.*?)\|'
                         r'(?P<full_path>.*?)\|'
                         r'(?P<headers>\{.*?\})'
                         )
        result = obj.finditer(line)
        for l in result:
            date = l.group('date')
            time = l.group('time')
            ip = l.group('ip')
            type = l.group('type')
            rulename = l.group('rulename')
            action = l.group('action')
            method = l.group('method')
            if method == "POST":

                pattern = re.compile(r'<QueryDict: \{.*?\}>')
                post = pattern.findall(line)
            else:
                post = ""

            path = l.group('path')
            full_path = l.group('full_path')
            headers = l.group('headers')
            id = date.replace("-", "") + "_" + time.replace(":", "").replace(",", "_") + "_" + ip.replace(".", "_")
            log = cls(date, time, ip, type, rulename, action, method, path, full_path, headers, id, file=None,
                      post=post)
            # 返回的是一个初始化后的类
            return log


def logRequest(request, config, action="unhandled", ):
    description = config['type']
    rule = config.name
    method = request.method
    path = request.path
    ip = getIp(request)

    if request.method == "GET":
        msg = ip + "|" + description + "-" + rule + "|" + action + "|" + method + "|" + path + "|" + urllib.parse.unquote(
            request.get_full_path()) + "|" + str(request.headers)
    elif request.method == "POST":
        msg = ip + "|" + description + "-" + rule + "|" + action + "|" + method + "|" + path + "|" + urllib.parse.unquote(
            request.get_full_path()) + "|" + str(request.headers) + "｜" + str(request.POST)

    logger.info(msg)

def add_pass_log(request,response):
    # amsterdam_timezone = pytz.timezone('Asia/Shanghai')
    # dt = amsterdam_timezone.localize(datetime.datetime.today())

    path = request.path
    ip = getIp(request)

    # 关于ip与真实ip还没搞清，参考https://falcon.readthedocs.io/en/stable/api/request_and_response_wsgi.html#

    # 获取ip

    if request.method == "GET":
        newpl = pass_log(ip=ip,time=datetime.datetime.today(),path=path,post="0", headers=str(request.headers)[0:255],status = response.status_code)
        newpl.save()

    elif request.method == "POST":
        newpl = pass_log(ip=ip,time=datetime.datetime.today(),path=path,post=str(request.POST)[0:127],headers = str(request.headers)[0:255],status = response.status_code)
        newpl.save()





# 从现在起回溯n分钟内非法访问次数
# pip install file-read-backwards文档倒读的库
from file_read_backwards import FileReadBackwards
import time
from interval import Interval
import datetime


def get_logByTimeIp(min, ip):  # 传入的参数为时间间隔和查找的ip
    end = datetime.datetime.now()  # 获取当前时间
    start = end - datetime.timedelta(minutes=min)  # 当前时间-min的时间
    time_interval = Interval(start, end)  # 构成一个min的时间区间
    log_list = []  # 存储符合条件的列表
    with FileReadBackwards(AR) as f:  # 采用FileReadBackwards读取log文件（非常规）
        for line in f:
            # 倒序逐个判断，若不符合条件就退出循环，不必判断log中的所有行
            # 判断是否在min内
            if line == "":
                continue
            if datetime.datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S') in time_interval:
                # 判断是否是该ip地址
                if line[24:33] == ip:
                    # 若是，放入log_list
                    log_list.append(line)
                else:  # 若不是，continue进行下一次判断
                    continue
                pass  # pass无实际意义，只是为了换行对齐
            else:  # 若不是在时间区间，直接跳出循环，因为是倒序读取
                break
            pass
        pass
    return log_list


def get_all_log():
    log_list = []
    with FileReadBackwards(AR) as f:  # 采用FileReadBackwards读取log文件（非常规）
        for line in f:
            if line == "":
                continue
            log = atklog.getByLine(line)
            log_list.append(log)
    return log_list


def get_log(ip="*", type="*"):
    log_list = []

    with FileReadBackwards(AR) as f:  # 采用FileReadBackwards读取log文件（非常规）
        for line in f:
            log = atklog.getByLine(line)
            # 筛选ip
            if ip != "*":
                if log.ip != ip:
                    continue
            # 筛选类型
            if type != "*":
                if log.type != type:
                    continue

            log_list.append(log)
    return log_list


def get_logByIp(ip, ):  # 传入的参数为时间间隔和查找的ip
    log_list = []  # 存储符合条件的列表
    with FileReadBackwards(AR) as f:  # 采用FileReadBackwards读取log文件（非常规）
        for line in f:
            if line[24:33] == ip:
                # 若是，放入log_list
                log_list.append(line)
            else:  # 若不是，continue进行下一次判断
                continue
        pass
    return log_list


def logAll(request):
    if request.method == "GET":

        msg = str(request.headers)
    elif request.method == "POST":
        msg = str(request.headers) + "|" + str(request.POST)
    logger.info(msg)


if __name__ == "__main__":
    # AR = "AttackRequest.log"
    atk = atklog.getByLine(
        "2022-10-25 13:50:03,469:127.0.0.1|SQL注入-sqli1|unhandled|GET|/secure/index/create database+||/secure/index/create database+|{'Content-Length': '', 'Content-Type': 'text/plain', 'Host': '127.0.0.1:8000', 'User-Agent': 'python-requests/2.28.1', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}:")
    print(atk.headers)
    a = eval(atk.headers)
    print(a['Host'])
