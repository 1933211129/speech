import configparser
import unittest
RCR = 'RequestCheckRule.ini'

def setRequestCheckRule(ruleName, re,new_name,u="0", cookie="0", p="0", h="0", dcp="无", type="未确定", Satus="1"):
    if ("#" in ruleName or ";" in ruleName):
        print(2)
        return 2
    config = configparser.ConfigParser()
    config.read(RCR)
    # 1.检查是否有此section
    if (ruleName in config):
        c = config[ruleName]
        new_name = "666"
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
        print(1)
        return 1
    print(0)
    return 0
if __name__ == '__main__':
    setRequestCheckRule(ruleName="sqli123",re="666")

