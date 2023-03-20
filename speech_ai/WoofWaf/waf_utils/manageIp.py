from WafMiddleware import models
def addBlackIp():
    models.ip_list.objects.create(ip="192.169.1.1", frequency=1.5, status=1, remain=60)

if __name__ == "__main__":
    models.ip_list.objects.create(ip="192.169.1.1",frequency=1.5,status=1,remain=60)