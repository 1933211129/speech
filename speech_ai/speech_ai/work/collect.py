import threading
import time
import os
from speech_ai.work.record import Recorder
from speech_ai.work.camera import cameraComput
from datetime import *


rec = Recorder()
cam = cameraComput()
name_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


class Collect:
    def fun1(self):
        rec.start()

    def fun2(self):
        path = 'E:/django_ai/speech_ai/speech_ai/work/record_wav/'+'0821.mp4'
        cam.saveVideo(path)

    def fun3(self):
        BASE_DIR = os.getcwd()
        music_name = 'E:/django_ai/speech_ai/speech_ai/work/record_wav/'+"0821.wav"
        rec.stop()
        print("stop:" + music_name)
        rec.save(music_name)
        path_audio = music_name
        print(path_audio)

    def start(self):
        obj1 = Collect()
        sing_thread = threading.Thread(target=obj1.fun1)
        song_thread = threading.Thread(target=obj1.fun2)

        sing_thread.start()
        song_thread.start()

    def stop(self):
        obj2 = Collect()
        sing_thread = threading.Thread(target=obj2.fun3)
        sing_thread.start()


