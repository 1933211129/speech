def check_file(request):
    if request.method == "POST":
        File = request.FILES.get("files", None)
        if File is not None:
            if not chkfiletype(File):
                return False
            if not chkfilecontent(File):
                return False

def chkfiletype(file):
    pass

def chkfilecontent(file):
    for line in file.readlines():
        line.decode("utf-8").replace('\\x', '%')
    pass

def chkfile(file):
    pass
