import datetime
import hashlib
import json
import os
import random
import shutil
import threading
import uuid
import cv2
import mediapipe as mp
import numpy as np
from deepface import DeepFace
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# 解决 Forbidden (CSRF token missing or incorrect.)
from django.views.decorators.csrf import csrf_exempt
from speech_ai import settings
from . import models
from .MyForms import *
from .fuc import findDb
from .py.Recorder import Recorder
from pathlib import Path

# 项目根目录
BaseDir = Path(__file__).resolve().parent.parent
BaseDir = str(BaseDir).replace('\\', '/')
print(BaseDir)

# 存放上一张图片的人体点位置
last_pose = {}


# 姿态识别和保存为图片， 返回姿态位置
def picture(read_file, save_file=''):
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(static_image_mode=True)

    image = cv2.imread(read_file)
    image_hight, image_width, _ = image.shape
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = holistic.process(image)

    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    # Lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    # Rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)

    annotated_image = image.copy()
    mp_drawing.draw_landmarks(annotated_image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    mp_drawing.draw_landmarks(annotated_image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(annotated_image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    if save_file != '':
        cv2.imwrite(save_file, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

    return pose.reshape(-1, 4)


stand_pose = picture(os.path.join(settings.MEDIA_ROOT, 'pose', '1.png').replace('\\', '/'))


# 测试网页html
def temp(request):
    if request.method == 'GET':
        return render(request, 'temp/temp.html')


# 文本评测
def txt(request, topic):
    # file_name = str(uuid.uuid4()).replace('-', '') + '.png'
    file_name = str(uuid.uuid4()).replace('-', '') + '.docx'
    if request.method == 'GET':
        return render(request, 'temp/temp.html')


# 开始录制
def start_record(request):  # pass  后端录制要改成前端录制
    # obj_record.start()
    response = HttpResponse(json.dumps({"status": 1}), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


# 结束录制
def stop_record(request):  # pass  后端录制要改成前端录制
    # obj_record.stop()
    response = HttpResponse(json.dumps({"status": 1}), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


# 姿态识别 、 表情识别
# @csrf_exempt
def speech(request):
    if request.session.get('user_name', None):
        if request.method == 'POST':
            backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe']
            user = models.MyUser.objects.get(username=request.session.get('user_name'))
            time = request.POST.get('time').replace('/', '-')
            time_name = time.replace(' ', '_').replace(':', '-')
            img_time = round(float(request.POST.get('imgTime')), 2)

            user_dir = os.path.join(settings.MEDIA_ROOT, 'pose', user.id).replace('\\', '/')
            date_dir = os.path.join(user_dir, time_name).replace('\\', '/')

            img_content = request.FILES.get('speech')
            if not os.path.isdir(user_dir):
                os.makedirs(user_dir)
            if not os.path.isdir(date_dir):
                os.makedirs(date_dir)

            file_name = request.POST.get('total') + '.png'
            file_name2 = request.POST.get('total') + '_' + '1' + '.png'

            file_path = date_dir + '/' + file_name
            save_file = date_dir + '/' + file_name2

            # with open(filePath, 'wb+') as f:
            #     for chunk in imgContent.chunks():
            #         f.write(chunk)
            default_storage.save(file_path, img_content)

            if request.POST.get('total') == '1':
                flag = True
                last_pose[user.id] = picture(file_path, save_file)
                score = poseScore(stand_pose, last_pose[user.id])

            else:
                test = picture(file_path, save_file)
                flag = Flag(last_pose[user.id], test)
                score = poseScore(stand_pose, test)
                last_pose[user.id] = test

            eps = DeepFace.analyze(img_path=file_path, detector_backend=backends[5], actions=('emotion',),
                                   enforce_detection=False)
            ret = {'eps': eps['dominant_emotion'], 'status': True, 'tip': '成功执行'}

            pose = models.Pose.objects.create(
                uid=user.id,
                img='/media/pose/' + user.id + '/' + time_name + '/' + file_name,
                pose='/media/pose/' + user.id + '/' + time_name + '/' + file_name2,
                score=score, emotion=ret['eps'],
                flag=flag, date=time, imgTime=img_time)
            pose.save()

            return JsonResponse(ret)
    else:
        return redirect("/login/tip/您还未登录 !/")


# 上传视频
def video(request):
    if request.method == 'POST':
        if request.session.get('user_name', None):
            user = models.MyUser.objects.get(username=request.session.get('user_name'))
            vid = request.FILES.get('video')
            videoExt = request.POST.get('videoExt')
            analyse_flag = request.POST.get('analyseFlag')
            time = request.POST.get('time').replace('/', '-')

            # 不存在则创建文件夹
            user_dir = os.path.join(settings.MEDIA_ROOT, 'pose', user.id).replace('\\', '/')
            time_name = request.POST.get('time').replace('/', '-').replace(' ', '_').replace(':', '-')
            date_dir = os.path.join(user_dir, time_name).replace('\\', '/')
            if not os.path.isdir(user_dir):
                os.makedirs(user_dir)
            if not os.path.isdir(date_dir):
                os.makedirs(date_dir)

            # 保存视频
            file_path = date_dir + '/1.' + str(videoExt)
            default_storage.save(file_path, ContentFile(vid.read()))

            # flag 为 true 进行分析
            if analyse_flag == 'true':
                # 创建音视频分析线程
                video_thread = threading.Thread(target=video_analyse, args=(file_path, date_dir, user.id, time))
                audio_thread = threading.Thread(target=audio_analyse, args=(file_path, user.id, time))

                # print(time, type(time))

                # 启动线程
                video_thread.start()
                audio_thread.start()
                # 等待所有线程完成
                video_thread.join()
                audio_thread.join()

            elif analyse_flag == 'false':
                audio_analyse(file_path, user.id, time)

            ret = {'tip': '分析完成', }
            return JsonResponse(ret)

        else:
            return redirect("/login/tip/您还未登录 !/")


# 音像分离
def convert_video_to_audio(file_path):
    from pydub import AudioSegment
    from pydub.exceptions import CouldntDecodeError
    import os

    file_ext = os.path.splitext(file_path)[1]
    try:
        audio = AudioSegment.from_file(file_path, file_ext[1:])
    except CouldntDecodeError:
        raise Exception(f" {file_ext} 格式不支持, 请使用 mp4, webm, flv 等视频格式")
    # Convert to mono
    audio = audio.set_channels(1)

    # Convert to 16kHz
    audio = audio.set_frame_rate(16000)

    # Save as WAV file
    new_file_path = file_path.split(".")[0] + ".wav"
    audio.export(new_file_path, format="wav")
    return new_file_path


def audio_analyse(file_path, uid, time):
    print('音频分析')
    # 提取音频
    audio_path = convert_video_to_audio(file_path)
    record = Recorder(audio_name=audio_path)
    final_result = record.Affix_and_evaluation()
    affix_score = final_result[0]
    xml_list = final_result[1]
    length = len(xml_list)

    # 存储分数
    fc_list = []
    ic_list = []
    pc_list = []
    tc_list = []
    for i in range(len(xml_list)):
        tmp_xml = record.get_xml_score(xml_list[i])
        fc_list.append(tmp_xml['fluency_score'])
        ic_list.append(tmp_xml['integrity_score'])
        pc_list.append(tmp_xml['phone_score'])
        tc_list.append(tmp_xml['tone_score'])

    fc_list = [float(i) for i in fc_list]
    ic_list = [float(i) for i in ic_list]
    pc_list = [float(i) for i in pc_list]
    tc_list = [float(i) for i in tc_list]

    fluency_score = round(sum(fc_list) / length, 2)
    integrity_score = round(sum(ic_list) / length, 2)
    phone_score = round(sum(pc_list) / length, 2)
    tone_score = round(sum(tc_list) / length, 2)
    total_score = round(fluency_score * 0.4 + integrity_score * 0.1 +
                        affix_score * 0.2 + phone_score * 0.15 + tone_score * 0.15, 2)

    speech_temp = models.Speach.objects.create(
        uid=uid, date=time, total_score=total_score,
        fluency_score=fluency_score, integrity_score=integrity_score,
        phone_score=phone_score, tone_score=tone_score, affix_score=affix_score,
        video_path=file_path.replace('\\', '/').replace(BaseDir, ''),
    )
    speech_temp.save()


# 本地视频分析
def video_analyse(file_path, date_dir, uid, time):
    video_path = file_path.replace('\\', '/')
    vid = cv2.VideoCapture(video_path)

    # 提取帧的频率
    frame_rate = vid.get(cv2.CAP_PROP_FPS)
    # 计算总帧数
    frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

    # 计算每一帧的时间
    frame_time = 1 / frame_rate
    # 每隔几秒截取一帧
    interval = 8
    # 计算每隔 interval 秒需要截取的帧数
    frames_to_capture = int(interval / frame_time)

    print(frame_count, frame_rate)

    count = 1
    for i in range(0, frame_count, frames_to_capture):
        random_frame_index = random.randint(i, i + frames_to_capture)
        vid.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)
        success, image = vid.read()
        if success:
            img_time = round(random_frame_index * frame_time, 2)

            file_path = os.path.join(date_dir, "{}.jpg".format(count)).replace('\\', '/')
            # cv2.imwrite(file_path, image)

            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            mp_holistic = mp.solutions.holistic
            holistic = mp_holistic.Holistic(static_image_mode=True)
            # image = cv2.imread(file_path)
            image_height, image_width, _ = image.shape
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)
            pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                             results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
            annotated_image = image.copy()
            mp_drawing.draw_landmarks(annotated_image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                      landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            mp_drawing.draw_landmarks(annotated_image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(annotated_image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            if pose.any() != 0:
                try:
                    backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe']
                    cv2.imwrite(file_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                    eps = DeepFace.analyze(img_path=file_path, detector_backend=backends[0], actions=('emotion',))
                    pose_path = os.path.join(date_dir, "{}_1.jpg".format(count)).replace('\\', '/')

                    cv2.imwrite(pose_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

                    if count == 1:
                        last_pose[uid] = pose.reshape(-1, 4)
                        flag = True
                    else:
                        test = pose.reshape(-1, 4)
                        flag = Flag(last_pose[uid], test)
                        last_pose[uid] = test

                    score = poseScore(stand_pose, pose.reshape(-1, 4))
                    pose = models.Pose.objects.create(
                        uid=uid,
                        # 标记
                        img=file_path.replace('\\', '/').replace(BaseDir, ''),
                        pose=pose_path.replace('\\', '/').replace(BaseDir, ''),
                        score=score, emotion=eps['dominant_emotion'],
                        flag=flag, date=time, imgTime=img_time)
                    pose.save()
                    count += 1
                except:
                    pass
            else:
                print("未识别到姿态")
        else:
            print('截取图像未成功')
    vid.release()


# 查分
def speachScore(request):
    if request.method == 'GET':
        uid = request.session.get('user_id')
        if uid:
            # user_name = request.session.get('user_name')
            dates = models.Speach.objects.filter(uid=uid).values('date').distinct()
            if len(dates) == 0:
                return redirect("/index/tip/请您先评测 !/")
            dates = [i['date'] for i in list(dates)]
            date = dates[-1]

            return redirect('/login/score/' + date.strftime('%Y-%m-%d_%H:%M:%S'))
        else:
            return redirect("/login/tip/您还未登录 !/")

    if request.method == 'POST':
        uid = request.session.get('user_id')
        date = request.POST.get('date')
        if uid:
            return redirect("/login/score/" + date.replace(' ', '_'))
        else:
            return redirect("/login/tip/您还未登录 !/")


def speachDateScore(request, date):
    if request.method == 'GET':
        uid = request.session.get('user_id')
        user_name = request.session.get('user_name')

        # date 进行处理
        date = datetime.datetime.strptime(date, '%Y-%m-%d_%H:%M:%S')
        # print(date)

        if uid:
            # 姿态
            exists = models.Speach.objects.filter(date=date).exists()

            if exists:
                dates = models.Speach.objects.filter(uid=uid).values('date').distinct()
                dates = [i['date'].strftime('%Y-%m-%d %H:%M:%S') for i in list(dates)]

                # 语音
                speech_table = list(models.Speach.objects.filter(uid=uid, date=date).values(
                    'content', 'fluency_score', 'integrity_score', 'phone_score', 'tone_score',
                    'affix_score', 'total_score', 'topic_score'))
                topic_score = speech_table[0]['topic_score']
                speech_table = [speech_table[0]['fluency_score'], speech_table[0]['integrity_score'],
                                speech_table[0]['phone_score'], speech_table[0]['tone_score'],
                                speech_table[0]['affix_score'], speech_table[0]['total_score'],
                                ]
                # 是否有主题契合度评分
                topic_flag = 'false'
                if topic_score is not None:
                    speech_table.append(topic_score)
                else:
                    topic_flag = 'true'

                pose = list(models.Pose.objects.filter(uid=request.session.get('user_id'), date=date)
                            .values('score', 'imgTime', 'pose', 'flag', 'emotion'))
                pose_score = [i['score'] for i in pose]
                imgTime = [i['imgTime'] for i in pose]
                flag = [str(i['flag']) for i in pose]
                emotion = [i['emotion'] for i in pose]
                dt = {'score': pose_score, 'imgTime': imgTime, 'emotion': emotion, 'flag': flag}

                # pose 图片 flag 为 1 是否超过一定数量，没超过则全部显示
                count_flag = False
                if flag.count('True') > 10:
                    count_flag = True

                # 返回
                return render(request, 'score/score.html',
                              {'login_status': True, 'user_name': user_name,
                               'date': date.strftime('%Y-%m-%d %H:%M:%S'), 'data': dt, 'speech_score': speech_table,
                               'content': speech_table, 'pose': pose, 'count_flag': count_flag,
                               'topic_flag': topic_flag, 'dates': dates})
            else:
                return HttpResponse('<h1>该日期下并没有评测 !</h1>')

        else:
            return redirect("/login/tip/您还未登录 !/")


# 展示 头像
def show_avatar(request):
    if request.session.get('user_name'):
        user = models.MyUser.objects.get(username=request.session.get('user_name'))
        avatar = user.avatar
        # user = models.Avatar.objects.filter(name='trent')[0]
        # avatarName = str(user.avatar)
        # avatarUrl = '%s/users/%s' % (settings.MEDIA_URL, avatarName) # 另一种写法
        # if request.method == 'GET':
        #     users = models.MyUser.objects.all()
        #     return render(request, 'login/show.html', {'avatar': avatar})
        return render(request, 'login/show.html', {'avatar': avatar, 'username': user.username})
        # avatar = os.path.join(settings.MEDIA_URL, 'photos/demo.png')
        # avatar_info = {'userName':str(image.user), 'avatarUrl': avatarUrl}
        # return render(request, 'login/show.html', {'avatar':avatar})
    else:
        return redirect("/login/tip/您还未登录 !/")


# 上传头像
def upload_avatar(request):
    if request.method == 'POST':
        if request.session.get('user_name', None):
            # image = models.MyUser(
            #     username = request.session.get('user_name'),
            #     avatar=request.FILES.get('avatar'),
            #     # face=request.FILES.get('face')
            # )
            user = models.MyUser.objects.get(username=request.session.get('user_name'))
            dire = os.path.join(settings.MEDIA_ROOT, 'avatar')
            img = request.FILES.get('avatar')
            fileName = user.id + '.' + img.name.split('.')[-1]
            filePath = os.path.join(dire, fileName).replace('\\', '/')
            # user.avatar.delete()
            if not os.path.isdir(dire):
                os.mkdir(dire)
            if os.path.exists(filePath):
                os.remove(filePath)
            with open(filePath, 'wb+') as f:
                for chunk in img.chunks():
                    f.write(chunk)
            user.avatar = 'avatar' + '/' + fileName
            user.save()
            # models.MyUser.objects.filter(id=user.id).update(avatar = 'avatar' + '/'+ fileName)
            return HttpResponse('<h1>' + request.session.get('user_name') + '</h1>')
        else:
            # return redirect('/login')
            return HttpResponse('<h1>user_name为空!</h1>')

    else:
        return render(request, 'login/upload_image.html')


# 用户信息
def user_info(request):
    if request.method == 'GET':
        if request.session.get('user_name'):
            user = models.MyUser.objects.get(username=request.session.get('user_name'))
            return render(request, 'user/info.html', {'user': user})
        else:
            return redirect("/login/tip/您还未登录 !/")

    # if request.method == 'POST':
    #     # 获取当前登录用户才能修改信息
    #     user = models.MyUser.objects.get(username=request.user.username)
    #     data = request.POST
    #     # print(request.FILES)
    #     avatar = request.FILES.get('avatar')
    #     # print(avatar)
    #     username = data.get("username")
    #     email = data.get("email")
    #     phone = data.get('phone')
    #     address = data.get('address')
    #     cate = data.get('cate')
    #     detail = data.get('detail')
    #     # 判断用户修改信息时，有没有上传新图片
    #     # 上传了换头像链接 否则不换
    #     # 无该判断时，若用户未更换图片，则原图片链接会被赋空值，导致头像丢失
    #     if avatar:
    #         u.avatar = avatar
    #     u.username = username
    #     u.email = email
    #     u.phone = phone
    #     u.address = address
    #     u.cate = cate
    #     u.detail = detail
    #     # 可能抛出异常：
    #     # 如果该用户修改的昵称已存在数据库中，会报错
    #     # 原因是，在我的设置里。用户名称是惟一的，不可重复的
    #     # 因此，避免bug，且提供给用户弹窗警告
    #     try:
    #         # 如果未获取当前用户，save会新建一个没有密码的用户，操作是错误的
    #         u.save()
    #     except:
    #         info = "该用户名已被注册"
    #         return render(request,'Myapp/error.html', {'info':info})
    #     # 和查看用户信息同理，每个用户都有自己的路由，修改后，重定向到新的路由
    #     # 因为该路由由用户名决定
    #     return HttpResponseRedirect('/profile/%s' % userinfo.username)
    # else:
    #     return render(request, 'Myapp/profile_edit.html', {'userinfo':userinfo})


# 求角度
def GetAngle(c1p1, c1p2, c2p1, c2p2):
    # 求出斜率
    if c1p2[0] == c1p1[0]:
        x = np.array([0, 1])
    else:
        k1 = (c1p2[1] - c1p1[1]) / (float(c1p2[0] - c1p1[0]))
        x = np.array([1, k1])
    if c2p2[0] == c2p1[0]:
        y = np.array([0, 1])
    else:
        k2 = (c2p2[1] - c2p1[1]) / (float(c2p2[0] - c2p1[0]))
        y = np.array([1, k2])
    # 模长
    Lx = np.sqrt(x.dot(x))
    Ly = np.sqrt(y.dot(y))
    # 根据向量之间求其夹角并保留固定小数位数
    Cobb = (np.arccos(x.dot(y) / (float(Lx * Ly))) * 180 / np.pi)
    return round(Cobb, 3)


# 四肢变换幅度界定 前后动作是否大
def Flag(sta, test):
    scope = 20
    flag_lst = [(11, 13), (13, 15), (12, 14), (14, 16), (24, 26), (26, 28), (23, 25), (25, 27)]
    for key in flag_lst:
        angle = GetAngle(sta[key[0]], sta[key[1]], test[key[0]], test[key[1]])
        if angle >= scope:
            return True
    return False


# 站姿正 得分
def poseScore(sta, test):
    scope = 20
    score = 0
    score_lst = [11, 12, 23, 24, 27, 28]
    for key in score_lst:
        angle = GetAngle(sta[key], sta[0], test[key], test[0])
        if abs(angle - scope) > scope:
            score += 0
        else:
            score += abs(angle - scope) / scope

    total_score = score / len(score_lst) * 100
    return round(total_score, 2)


# 上传 人脸图片
def face_upload(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            user_name = request.session.get('user_name')
            return render(request, 'face/upload.html', {'login_status': True, 'user_name': user_name, 'page': 'upload'})

        if request.method == 'POST':
            user = models.MyUser.objects.get(username=request.session.get('user_name'))
            dirFace = os.path.join(settings.MEDIA_ROOT, 'face', user.id).replace('\\', '/')
            imgs = request.FILES.getlist('face')

            if os.path.isdir(dirFace):
                # 如果目标路径存在原文件夹的话就先删除
                shutil.rmtree(dirFace)

            os.makedirs(dirFace)

            for img in imgs:
                # 后缀名
                # fileName = str(uuid.uuid4()).replace('-', '') + '.' + img.name.split('.')[-1]
                file_name = str(uuid.uuid4()).replace('-', '') + '.png'
                filePath = os.path.join(dirFace, file_name).replace('\\', '/')
                with open(filePath, 'wb+') as f:
                    for chunk in img.chunks():
                        f.write(chunk)

            if os.path.exists('./media/face/representations_vgg_face.pkl'):
                os.remove('./media/face/representations_vgg_face.pkl')
            findDb.findDb(db_path='./media/face', enforce_detection=False, distance_metric='euclidean')

            ret = {'status': True}
            return JsonResponse(ret)

    else:
        return redirect("/login/tip/您还未登录 !/")
        # return redirect('/login')


# 人脸登录
def face_login(request):
    if request.session.get('is_login', None):
        return redirect("/index/tip/您已登录 !/")

    else:
        if request.method == 'GET':
            return render(request, 'face/face_login.html', {'page': 'login'})

        if request.method == 'POST':
            dr = os.path.join(settings.MEDIA_ROOT, 'temp').replace('\\', '/')
            model_name = ['VGG-Face', 'Facenet', 'OpenFace', 'DeepFace', 'DeepID', 'Dlib', 'Ensemble']
            img = request.FILES.get('face')
            fileName = str(uuid.uuid4()).replace('-', '') + '.png'
            filePath = os.path.join(dr, fileName).replace('\\', '/')
            with open(filePath, 'wb+') as f:
                for chunk in img.chunks():
                    f.write(chunk)
            df = DeepFace.find(img_path=filePath, model_name=model_name[0], db_path='./media/face',
                               enforce_detection=False, distance_metric='euclidean')

            os.remove(filePath)

            if df.iloc[0]['VGG-Face_euclidean'] < 0.35:
                uid = df.iloc[0]['identity'].replace('\\', '/').split('/')[-2]
                if models.MyUser.objects.get(id=uid):
                    user = models.MyUser.objects.get(id=uid)
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.username
                    request.session['status_flag'] = user.status_flag

                    ret = {'state': True, 'user_name': str(user.username)}
                    return JsonResponse(ret)

                else:
                    ret = {'state': False}
                    return JsonResponse(ret)

            else:
                ret = {'state': False}
                return JsonResponse(ret)


# 登录 邮箱、用户名、密码、验证码
def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/tip/您已登录/")

    elif request.method == "GET":
        print(request.session.get('is_login'))
        register_form = RegisterForm()
        login_form = LoginForm()
        login_message = ""
        return render(request, 'login/login.html',
                      {'login': True, 'login_form': login_form, 'register_form': register_form,
                       'login_message': login_message})

    elif request.method == "POST":
        register_form = RegisterForm()
        login_form = LoginForm(request.POST)
        login_message = "表单验证失败"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            flag = login_form.cleaned_data['flag']

            if models.MyUser.objects.filter(username=username).exists():
                user = models.MyUser.objects.get(username=username)

                if user.status_flag == flag:
                    if user.password == hash_code(password):
                        request.session['is_login'] = True
                        request.session['user_id'] = user.id
                        request.session['user_name'] = user.username
                        request.session['status_flag'] = user.status_flag

                        # 普通用户
                        if user.status_flag == '0':
                            return redirect("/index/")
                        # 裁判
                        elif user.status_flag == '1':
                            return redirect("/judge/video/")
                        # 管理员
                        elif user.status_flag == '2':
                            return redirect("/Administrator/secure/index")
                    #     /Administrator/secure/index

                    else:
                        login_message = "密码不正确"
                else:
                    login_message = "请选择正确的用户身份"
            else:
                login_message = "用户不存在"
        # return render(request, 'login/login.html', locals())
        return render(request, 'login/login.html',
                      {'login': True, 'login_form': login_form, 'register_form': register_form,
                       'login_message': login_message})


# 登录 提示
def login_tip(request, tip):
    if request.method == "GET":
        register_form = RegisterForm()
        login_form = LoginForm()
        return render(request, 'login/login.html',
                      {'login': True, 'login_form': login_form, 'register_form': register_form,
                       'login_message': None, 'tip': tip})


# 注册 邮箱、用户名、密码、验证码
def register(request):
    if request.session.get('is_login', None):
        return redirect("/index/tip/您已登录/")

    elif request.method == "GET":
        register_form = RegisterForm()
        login_form = LoginForm()
        login_message = ""
        return render(request, 'login/login.html',
                      {'login': False, 'login_form': login_form, 'register_form': register_form,
                       'login_message': login_message})

    elif request.method == "POST":
        login_form = LoginForm()
        register_form = RegisterForm(request.POST)
        register_message = "表单验证失败"
        if register_form.is_valid():
            email = register_form.cleaned_data['email']
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            password2 = register_form.cleaned_data['password2']
            if password != password2:
                register_message = '两次密码不一样'
                return render(request, 'login/login.html',
                              {'login': False, 'register_form': register_form, 'login_form': login_form,
                               'register_message': register_message})

            elif models.MyUser.objects.filter(email=email).exists():
                register_message = '邮箱已注册'
                return render(request, 'login/login.html',
                              {'login': False, 'register_form': register_form, 'login_form': login_form,
                               'register_message': register_message})

            elif models.MyUser.objects.filter(username=username).exists():
                register_message = '用户名已注册'
                return render(request, 'login/login.html',
                              {'login': False, 'register_form': register_form, 'login_form': login_form,
                               'register_message': register_message})
            else:
                user = models.MyUser.objects.create(username=username, email=email, password=hash_code(password))
                user.save()
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username
                # return redirect("/index", login_status=True)
                return redirect("/index/")
                # return render(request, "index.html", {'login_status': True, 'user_name': str(user.username)})

        return render(request, 'login/login.html',
                      {'login': False, 'register_form': register_form, 'login_form': login_form,
                       'register_message': register_message})


# 注销
def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/login/tip/您还未登录 !")

    request.session.flush()
    return redirect("/login")


# 字符串+哈希
def hash_code(s, salt='speech_ai'):  # 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


# 返回登录注册页面
def login_register(request):
    if request.session.get('is_login', None):
        return redirect("/index/tip/您已登录/")

    elif request.method == "GET":
        login_form = LoginForm()
        register_form = RegisterForm()
        return render(request, 'login/login.html',
                      {'login': True, 'login_form': login_form, 'register_form': register_form})


# 返回 404 页面
def page_not_found(request, exception):
    return render(request, '404.html')

# 500
# def page_error(request, exception):
#     return render(request, '404.html')


#
# # 历史得分 页面
# def history_score(request):
#     if request.method == 'GET':
#         uid = request.session.get('user_id')
#         if uid:
#             user_name = request.session.get('user_name')
#
#             dates = models.Speach.objects.filter(uid=uid).values('date').distinct()
#             dates = [i['date'] for i in list(dates)]
#             if len(dates) == 0:
#                 return redirect("/index/tip/请您先评测 !/")
#
#             poses = []
#             speach = []
#             for date in dates:
#                 poses.append(pose_query(uid, date))
#                 speach.append(speach_query(uid, date))
#             dates = [x.strftime('%Y-%m-%d %H:%M:%S') for x in dates]
#
#             return render(request, 'score/HistoryScore.html',
#                           {'login_status': True, 'user_name': user_name, 'poses': poses, 'dates': dates,
#                            'speach': speach})
#         else:
#             return redirect("/login/tip/您还未登录 !/")
#
#
# # 查询pose表函数
# def pose_query(user_id, date):
#     data = list(
#         (models.Pose.objects.filter(uid=user_id, date=date)).values('score', 'imgTime', 'pose', 'flag', 'emotion'))
#     score = [i['score'] for i in data]
#     imgTime = [i['imgTime'] for i in data]
#     pose_img = [i['pose'] for i in data]
#     flag = [str(i['flag']) for i in data]
#     emotion = [i['emotion'] for i in data]
#     dic = {'score': score, 'imgTime': imgTime, 'pose_img': pose_img, 'flag': flag, 'emotion': emotion}
#     return dic
#
#
# # 查询speach表函数
# def speach_query(user_id, date):
#     data = list(
#         (models.Speach.objects.filter(uid=user_id, date=date)).values('total_score', 'content', 'fluency_score',
#                                                                       'integrity_score', 'phone_score', 'tone_score',
#                                                                       'topic_score', 'affix_score'))
#     data = [data[0]['content'], data[0]['total_score'], data[0]['fluency_score'],
#             data[0]['integrity_score'], data[0]['phone_score'], data[0]['tone_score'],
#             data[0]['topic_score'], data[0]['affix_score'],
#     ]
#     return data
#
