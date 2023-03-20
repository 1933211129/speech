# 本文件编写 从config中取出正则表达式并匹配参数的方法，需要返回匹配出的攻击类型
# 目前还未编写config文件，先匹配静态的列表

import requests
from urllib.parse import urlparse
from re import match

import logging



if __name__ == "__main__":
    import requests

    url="http://127.0.0.1:8000/secure/index/"
    for i in range (1,10) :
        requests.get(url)
        print(requests.status_codes)




