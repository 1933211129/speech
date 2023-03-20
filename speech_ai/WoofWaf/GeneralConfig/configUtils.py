import configparser


# 获取DEFAULT
def getDefault(configpath):
    config = configparser.ConfigParser()
    config.read(configpath)
    return config['DEFAULT']


# 转换状态
def swtichStatus(configpath,section,field):
    config = configparser.ConfigParser()
    config.read(configpath)
    if config.get(section,field) == "1":
        with open(configpath, "w") as f:
            config.set(section, field, "0")
            config.write(f)
    else:
        with open(configpath, "w") as f:
            config.set(section, field, "1")
            config.write(f)



# 删除某section
def delConfig(configpath,section):
    config = configparser.ConfigParser()
    config.read(configpath)
    if (section in config):
        with open(configpath,"w") as f:
            config.remove_section(section)
            config.write(f)
            return 0
    else:
        return 1

# 更改某filed的值
def setField(configpath,section,field,newkey):
    config = configparser.ConfigParser()
    config.read(configpath)
    with open(configpath, "w") as f:
        config.set(section, field, newkey)
        config.write(f)


# 检查请求时只查看开启的规则
# 返回的列表里装的configPaser.proxy
def getOpenRule(configpath):
    config = configparser.ConfigParser()
    config.read(configpath)
    configlist = []
    for section in config.sections():
        if config[section]['status'] == "1":
            configlist.append(config[section])
        else:
            continue
    return configlist

# 管理时返回全部规则
def getAllRule(configpath):
    config = configparser.ConfigParser()
    config.read(configpath)
    configlist = []
    for section in config.sections():
            configlist.append(config[section])
    return configlist

# 返回的列表装的dict,已弃用
def getAllRule1(configpath):
    config1 = configparser.ConfigParser()
    config1.read(configpath)
    configlist = []
    for section in config1.sections():
        config = config1[section]
        checkRange = ""
        if config['chkurl']=="1":
            checkRange.join("URL,")
        if config['chkcookie'] == "1":
            checkRange.join("COOKIE,")
        if config['chkpost'] == "1":
            checkRange.join("POST,")
        if config['chkheader'] != "0":
            checkRange.join("HEADERS,")
        configdict = {'name':config.name,
                      'status' : config['status'],
                      'chkrul': config['chkurl'],
                      'chkcookie': config['chkcookie'],
                      'chkpost': config['chkpost'],
                      'chkheader': config['chkheader'],
                      'regex': config['regex'],
                      'dcp': config['dcp'],
                      'type': config['type'],
                      'surl':"/secure/"+config.name+"/HttpCheckSwitched/",
                      }
        configlist.append(configdict)
    return configlist

