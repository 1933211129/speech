from WoofWaf.models import defend_log, pass_log


def get_defend_log(ip="*"):
    if ip == "*":
        queryset =defend_log.objects.all()
    else:
        queryset = defend_log.objects.filter(ip=ip)
    return queryset

def get_pass_log(ip="*"):
    if ip == "*":
        queryset =pass_log.objects.all()
    else:
        queryset = pass_log.objects.filter(ip=ip)
    return queryset