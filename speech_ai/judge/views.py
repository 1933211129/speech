import json
from django.http import JsonResponse
from speech_ai import settings
from django.shortcuts import render, redirect, HttpResponse
from .Form import VideoForm, RaceForm
from .models import Competitor, Race

# 解决 Forbidden (CSRF token missing or incorrect.)
from django.views.decorators.csrf import csrf_exempt
import datetime
from pathlib import Path
import os
import subprocess
import numpy as np

BaseDir = Path(__file__).resolve().parent.parent
BaseDir = str(BaseDir).replace('\\', '/')


# 最终分数
def finalScore(request):
    if request.method == 'GET':
        uid = request.session.get('user_id')
        if uid:
            user_name = request.session.get('user_name')
            exist = Race.objects.filter(OrganizerID=uid).exists()
            if exist:
                race = Race.objects.get(OrganizerID=uid)
                cptrs = Competitor.objects.filter().values('Cptr_Name', 'HumanScore', 'VoiceScore', 'PoseScore').distinct()

                dic = {}
                for cptr in cptrs:
                    if cptr['HumanScore'] is not None:
                        cptr['HumanScore'] = json.loads(cptr['HumanScore'])
                    if cptr['VoiceScore'] is not None:
                        cptr['VoiceScore'] = json.loads(cptr['VoiceScore'])
                    if cptr['PoseScore'] is not None:
                        cptr['PoseScore'] = json.loads(cptr['PoseScore'])
                    if cptr['HumanScore'] == None:
                        dic[cptr['Cptr_Name']] = (np.array(cptr['VoiceScore']).mean() * 1 +
                                                  np.array(cptr['PoseScore']).mean() * 3
                                                  ) / 4
                    else:
                        dic[cptr['Cptr_Name']] = (np.array(cptr['HumanScore']).mean() * 1 +
                                                  np.array(cptr['VoiceScore']).mean() * 1 +
                                                  np.array(cptr['PoseScore']).mean() * 3
                                                  ) / 5
                sorted_dict = {k: v for k, v in sorted(dic.items(), key=lambda item: item[1], reverse=True)}
                name = []
                score = []
                for k, v in sorted_dict.items():
                    name.append(k)
                    score.append(v)

                return render(request, 'judge/FinalScore.html', {'login_status': True, 'user_name': user_name,
                                                                 'race_name': race.race_name, 'name': name,
                                                                 'score': score})

            else:
                return HttpResponse('您并不是赛事组织者')



        else:
            return HttpResponse('请先登录 !')


# 人工评分上传
def HumanScore(request):
    if request.method == 'POST':
        uid = request.session.get('user_id')
        # print(uid)
        if uid:
            race = Race.objects.get(OrganizerID=uid)
            cptr_id = request.POST.get('cptrID')
            qinggan = request.POST.get('qinggan')
            ziti = request.POST.get('ziti')
            luoji = request.POST.get('luoji')
            wencai = request.POST.get('wencai')

            # print(race.race_id)
            # print(cptr_id)
            # print([qinggan, ziti, luoji, wencai])

            cptr = Competitor.objects.get(race_id=race.race_id, Cptr_id=cptr_id)
            cptr.HumanScore = json.dumps([float(qinggan), float(ziti), float(luoji), float(wencai)])
            cptr.save()

        else:
            return HttpResponse('请先登录 !')

        ret = {'tip': '分析完成'}
        return JsonResponse(ret)


# 视频人工打分
def videoScore(request):
    if request.method == 'GET':
        if request.session.get('is_login', None):
            # 已登录
            user_name = request.session.get('user_name')
            uid = request.session.get('user_id')

            # 判断是否有比赛
            exist = Race.objects.filter(OrganizerID=uid).exists()
            if exist:

                # flag判断是否通过申请
                # if race.flag == False:
                #     return HttpResponse('比赛申请还未通过 !')
                # else:
                competitors = Competitor.objects.filter(race_id=Race.objects.get(OrganizerID=uid).race_id).values(
                    'race_id', 'Cptr_id', 'Cptr_Name', 'video_path', 'img_path', 'video_upload_date').distinct()

                return render(request, 'judge/judge_video.html',
                              {'login_status': True, 'user_name': user_name, 'competitors': competitors}
                              )

            else:
                return HttpResponse('请你先申请比赛 !')

        # 未登录
        return redirect("/login/tip/您还未登录 !/")



# 视频提交页面
def submit(request):
    message = ''
    if request.method == 'GET':
        video_form = VideoForm()
        # 是否登录
        if request.session.get('is_login', None):
            user_name = request.session.get('user_name')

            # 测试 图片生成

            return render(request, 'judge/AdemoVideo.html', {'login_status': True, 'user_name': user_name,
                                                             'video_form': video_form, 'message': message})
        else:
            # return HttpResponse('未登录')
            return redirect("/login/tip/您还未登录 !/")


# 视频提交请求
# @csrf_exempt  # 禁止跨域检查
def videoSubmit(request):
    if request.method == 'POST':
        if request.session.get('is_login', None):
            user_name = request.session.get('user_name')
            video_form = VideoForm(request.POST, request.FILES)  # 注意要有 request.POST, request.FILES

            # 判断表单是否有误
            if video_form.is_valid():
                raceID = video_form.cleaned_data['raceID']

                # try:

                # 查看赛事码是否在赛事表中
                exist = Race.objects.filter(race_id=raceID).exists()

                if exist:
                    # 获得选手id
                    Cptr_id = request.session.get('user_id')

                    # 选手重复上传视频
                    exist = Competitor.objects.filter(race_id=raceID, Cptr_id=Cptr_id).exists()
                    if exist:
                        message = '选手不能重复上传视频 !'
                        return render(request, 'judge/AdemoVideo.html', {'login_status': True, 'user_name': user_name,
                                                                         'video_form': video_form,
                                                                         'message': message})
                    else:
                        # 获得表单
                        name = video_form.cleaned_data['name']
                        gender = video_form.cleaned_data['gender']
                        phone = video_form.cleaned_data['phone']
                        email = video_form.cleaned_data['email']
                        unit = video_form.cleaned_data['unit']
                        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        video = request.FILES['video']

                        cptr = Competitor.objects.create(
                            race_id=raceID, Cptr_id=Cptr_id,
                            Cptr_Name=name, Cptr_gender=gender,
                            Cptr_phone=phone, Cptr_email=email, Cptr_unit=unit,
                            video_upload_date=time, video_path=video
                            # , img_path=img
                        )
                        cptr.save()

                        user_id = request.session.get('user_id')
                        user_dir = os.path.join(settings.MEDIA_ROOT, 'pose', user_id).replace('\\', '/')
                        time_name = time.replace(' ', '_').replace(':', '-')
                        date_dir = os.path.join(user_dir, time_name).replace('\\', '/')

                        if not os.path.isdir(user_dir):
                            os.makedirs(user_dir)
                        if not os.path.isdir(date_dir):
                            os.makedirs(date_dir)

                        file_path = os.path.join(BaseDir, 'media', str(cptr.video_path)).replace('\\', '/')

                        subprocess.Popen(['python', BaseDir + '/judge/work/analyze_video_file.py',
                                          file_path, date_dir, user_id, time, raceID])

                        # print(file_path, date_dir, user_id, time, raceID)
                        # analyze_video_file(file_path, date_dir, user_id, time, raceID)

                        return redirect("/index/tip/申请提交成功 !/")

                else:
                    message = '赛事码有误 !'
                    return render(request, 'judge/AdemoVideo.html', {'login_status': True, 'user_name': user_name,
                                                                     'video_form': video_form, 'message': message})

            else:
                print(video_form.errors)
                message = '出现问题，请刷新页面重新上传'
                return render(request, 'judge/AdemoVideo.html', {'login_status': True, 'user_name': user_name,
                                                                 'video_form': video_form, 'message': message})
        else:
            return redirect("/login/tip/请先登录 !/")


# 得到分数
# def get_Score(request):
# competitor = Competitor.objects.get(race_id=raceID, Cptr_id=Cptr_id)
# lst2 = json.loads(competitor.HumanScore)


# 赛事申请
def RaceApplication(request):
    message = ''
    if request.method == 'GET':
        # 是否登录
        if request.session.get('is_login', None):
            race_form = RaceForm()
            user_name = request.session.get('user_name')
            return render(request, 'judge/AdemoRace.html', {'login_status': True, 'user_name': user_name,
                                                            'race_form': race_form, 'message': message})
        else:
            return redirect("/login/tip/您还未登录 !/")

    elif request.method == 'POST':
        # 是否登录
        if request.session.get('is_login', None):
            uid = request.session.get('user_id')
            race_form = RaceForm(request.POST, request.FILES)

            if race_form.is_valid():
                race_name = race_form.cleaned_data['race_name']
                race_time = race_form.cleaned_data['race_time']
                # race_file = request.FILES['race_file']

                organizers_mobile = race_form.cleaned_data['organizers_mobile']
                organizers_email = race_form.cleaned_data['organizers_email']
                organizers_unit = race_form.cleaned_data['organizers_unit']

                race = Race.objects.create(
                    OrganizerID=uid, organizers_mobile=organizers_mobile,
                    organizers_email=organizers_email, organizers_unit=organizers_unit,
                    race_name=race_name, race_time=race_time,
                    # race_file=race_file
                )
                race.save()
                return redirect("/index/tip/申请提交成功 !/")

            else:
                message = race_form.errors
                print(race_form.errors)
                return render(request, 'judge/AdemoRace.html',
                              {'video_form': race_form, 'message': message})

        else:
            return redirect("/login/tip/您还未登录 !/")


def Competition_application(request):
    return render(request, 'judge/Competition_application.html')


def homepage(request):
    if request.method == 'GET':
        if request.session.get('is_login', None):
            user_name = request.session.get('user_name')
            return render(request, 'judge/homepage.html', {'login_status': True, 'user_name': user_name})
        else:
            return redirect("/login/tip/您还未登录 !/")


def signup(request):
    return render(request, 'judge/SignUp.html')


def contact(request):
    if request.session.get('is_login', None):
        user_name = request.session.get('user_name')
        return render(request, 'judge/contact.html', {'login_status': True, 'user_name': user_name})
    return render(request, 'judge/contact.html', {'login_status': False})


def index(request):
    videos = Competitor.objects.all()
    context = {
        'videos': videos
    }
    return render(request, 'judge/index.html', context)


# 传入视频路径，随机截取帧画面
def extract_frame(video_path):
    import cv2
    import os
    import random

    # Read the video
    cap = cv2.VideoCapture(video_path)

    # Get a random frame
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    random_frame_index = int(total_frames * random.random())
    cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)
    ret, frame = cap.read()

    # Resize the frame to 320x320
    resized_frame = cv2.resize(frame, (320, 320))

    # Get the video name without extension
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    # Save the frame as a JPEG file with the same name as the video in the same directory
    # frame_path = './speech/frame/'+ video_name + '.jpg'
    frame_path = os.path.join(os.path.dirname(video_path) + '/frame/' + video_name + '.jpg')
    cv2.imwrite(frame_path, resized_frame)

    # Release the video capture
    cap.release()
    return frame_path


# 调取视频和帧画面显示在评委评分页面
def video_index(request):
    videos = Competitor.objects.all()
    video_properties = []

    for video in videos:
        video_path = video.video_path
        video_title = video.title
        video_frame = video.frame_path
        video_properties.append({
            'title': video_title,
            'path': video_path,
            'thumbnail': video_frame,
        })
    context = {'video_properties': video_properties}
    return render(request, 'judge/judge_video.html', context)


# “火热进行”页面表格
def show_events(request):
    # Get all competitions whose race time is after today's date
    events = Race.objects.all()

    # Render the HTML template and pass the events as context
    return render(request, 'judge/event_list.html', {'events': events})
