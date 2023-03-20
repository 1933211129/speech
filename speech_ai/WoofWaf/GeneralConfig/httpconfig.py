import configparser

from WoofWaf.GeneralConfig.configUtils import delConfig

# https://docs.python.org/zh-cn/3/library/configparser.html
RCR="WoofWaf/GeneralConfig/RequestCheckRule.ini"

def createconfRCR():
    # 1
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'RequestCheck': '1',
                         }
    # 2
    config['sqli1'] = {}
    config['sqli1']['Status'] = '1'
    config['sqli1']['ChkUrl'] = '1'
    config['sqli1']['ChkCookie'] = '0'
    config['sqli1']['ChkPost'] = '1'
    config['sqli1']['ChkHeader'] = 'User-Agent Accept'
    config['sqli1']['Regex'] = r'\b(create|drop|backup)\b(\+| )+\bdatabase\b(\+| )+\w*'
    config['sqli1']['Dcp'] = '防止对数据库进行创建、删除、备份操作'
    config['sqli1']['Type'] = 'Sql注入'


    # 以上使用了三种方法写入配置文件
    with open('RequestCheckRule.ini', 'w') as configfile:
        config.write(configfile)


def addRequestCheckRule(ruleName, re,u="0", cookie="0", p="0", h="0", dcp="无", type="未确定", Satus="1"):
    if ("#" in ruleName or ";" in ruleName):
        return 2
    config = configparser.ConfigParser()
    config.read(RCR)
    # 1.检查是否有重名section
    if (ruleName in config):
        return 1
    else:
        config[ruleName] = {}
        c = config[ruleName]
        c['Status'] = Satus
        c['ChkUrl'] = u
        c['ChkCookie'] = cookie
        c['ChkPost'] = p
        c['ChkHeader'] = h
        c['Regex'] = re
        c['Dcp'] = dcp
        c['Type'] = type
        with open(RCR, 'w') as configfile:
            config.write(configfile)
    return 0

def setRequestCheckRule(ruleName, new_name,re,u="0", cookie="0", p="0", h="0", dcp="无", type="未确定", Satus="1"):
    if ("#" in ruleName or ";" in ruleName):
        return 2
    config = configparser.ConfigParser()
    config.read(RCR)
    # 1.检查是否有此section
    if (ruleName in config):
        c = config[ruleName]
        c['Status'] = Satus
        c['ChkUrl'] = u
        c['ChkCookie'] = cookie
        c['ChkPost'] = p
        c['ChkHeader'] = h
        c['Regex'] = re
        c['Dcp'] = dcp
        c['Type'] = type
        config._sections[new_name] = config._sections.pop(ruleName)
        with open(RCR, 'w') as configfile:
            config.write(configfile)
    else:
        return 1

    return 0





# 重写整个section（删除又添加）
def resetConfig(ruleName, re, path,u="0", cookie="0", p="0", h="0", dcp="无", type="未确定", Satus="1"):
    delConfig(path,ruleName)
    addRequestCheckRule(ruleName, re, path,u, cookie, p, h, dcp, type,Satus)




def readconf():
    config = configparser.ConfigParser()
    print(config.sections())
    # 未读文件，输出空列表

    config.read('example.ini')

    print(config.sections())
    # 读文件后输出所有section

    # 判断config中是否存在section
    print('bitbucket.org' in config)

    print('bytebong.com' in config)
    # 判断是否存在字段
    print(config['bitbucket.org']['User'])

    print(config['DEFAULT']['Compression'])
    # 输出字段值
    topsecret = config['topsecret.server.com']
    print(topsecret['ForwardX11'])

    print(topsecret['Port'])

    for key in config['bitbucket.org']:
        print(key)

    print(config['bitbucket.org']['ForwardX11'])

if __name__ == "__main__":

    # createconfRCR()
    # config = configparser.ConfigParser()
    # config.read('RequestCheckRule.ini')
    # print(config.sections())
    # # delConfig('RequestCheckRule.ini','sqli123')
    # print(config['sqli123']['status']+config['sqli1']['chkurl'])
    # resetField('RequestCheckRule.ini','sqli123','chkheader','0')
    # for i in range(101):
    #     swtichStatus('RequestCheckRule.ini','sqli123','status')
    pass