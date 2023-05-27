import json
import random
import threading
import sys
from pathlib import Path
import django


# 项目根目录
BaseDir = Path(__file__).resolve().parent.parent.parent
BaseDir = str(BaseDir).replace('\\', '/')
sys.path.append(BaseDir)
django.setup()


from judge.models import Competitor
from login.models import Pose, Speach, MyUser
from login.views import video_analyse, audio_analyse
import datetime
import cv2
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile


def analyze_video_file(file_path, date_dir, userID, time, raceID):
    # 创建音视频分析线程
    video_thread = threading.Thread(target=video_analyse, args=(file_path, date_dir, userID, time))
    audio_thread = threading.Thread(target=audio_analyse, args=(file_path, userID, time))
    # 启动线程
    video_thread.start()
    audio_thread.start()
    # 等待所有线程完成
    video_thread.join()
    audio_thread.join()

    date = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    pose = Pose.objects.filter(uid=userID, date=date).values('score').distinct()
    pose_lst = [i['score'] for i in pose]

    voice = Speach.objects.get(uid=userID, date=date)
    if voice.topic_score is not None:
        voice_lst = [voice.fluency_score, voice.integrity_score, voice.phone_score, voice.tone_score, voice.affix_score,
                     voice.topic_score]
    else:
        voice_lst = [voice.fluency_score, voice.integrity_score, voice.phone_score, voice.tone_score, voice.affix_score]

    competitor = Competitor.objects.get(race_id=raceID, Cptr_id=userID, video_upload_date=date)
    competitor.PoseScore = json.dumps(pose_lst)
    competitor.VoiceScore = json.dumps(voice_lst)

    # 截取图片
    vid = cv2.VideoCapture(file_path)
    frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    random_frame_index = random.randint(0, frame_count)
    vid.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)
    success, image = vid.read()
    if success:
        image = cv2.resize(image, (320, 320))
        _, img_encoded = cv2.imencode('.jpg', image)
        img_content = ContentFile(img_encoded.tobytes())
        img_file = InMemoryUploadedFile(img_content, None, 'image.jpg', 'image/jpeg', img_content.tell(), None)
        competitor.img_path = img_file
    vid.release()

    competitor.save()

    # 更改用户身份为 裁判
    # user = MyUser.objects.get(id=userID)
    # user.status_flag = 1
    # user.save()

    print('视频分析完成.')


if __name__ == '__main__':
    analyze_video_file(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
