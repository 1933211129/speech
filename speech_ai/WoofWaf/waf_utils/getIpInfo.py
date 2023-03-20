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



