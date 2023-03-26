import time
a = "2023-02-27_17:27:38"
a = a.replace('_', ' ')
b=time.strptime(a,'%Y-%m-%d %H:%M:%S')
#转换为时间组对象

print(b)