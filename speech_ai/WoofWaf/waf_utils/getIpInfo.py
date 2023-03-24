import requests
import json

from WoofWaf.models import ip_list


def getIp(request):
    if request.META.get("access_route") is None:
        ip = request.META.get("REMOTE_ADDR")
    else:
        ip = request.META.get("access_route")
    return ip
def ipInfo(ipaddress):
    url = 'http://ip.taobao.com/service/getIpInfo.php?ip=' + ipaddress
    rsp = requests.get(url)
    json = rsp.json()
    print(json)
    # data=content.text
    # jsondata = json.loads(data)
    # print(jsondata)
    # if jsondata[u'code'] == 0:
    #     print ('所在国家：' + jsondata[u'data'][u'country'].encode('utf-8'))
    #     print ('所在地区：' + jsondata[u'data'][u'area'].encode('utf-8'))
    #     print ('所在省份：' + jsondata[u'data'][u'region'].encode('utf-8'))
    #     print ('所在城市：' + jsondata[u'data'][u'city'].encode('utf-8'))
    #     print ('所用运营商：' + jsondata[u'data'][u'isp'].encode('utf-8'))
    # else:
    #     print ('查询失败 请检查IP 后再说')

#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib2
from urllib.parse import urlencode #python3
#from urllib import urlencode #python2
params = urlencode({'ip':'9.8.8.8','datatype':'jsonp','callback':'find'})
url = 'https://api.ip138.com/ip/?'+params
headers = {"token":"8594766483a2d65d76804906dd1a1c6a"}#token为示例
http = httplib2.Http()
response, content = http.request(url,'GET',headers=headers)
print(content.decode("utf-8"))

