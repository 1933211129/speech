# -*- coding: utf-8 -*-
from platform import release
import cv2
import time


# 定义摄像头类
class cameraComput(object):
    def __init__(self):
        # 获取摄像头对象，0 系统默认摄像头
        self.cap = cv2.VideoCapture(0)
        # 判断摄像头是否打开，没有则打开
        if not self.cap.isOpened():
            self.cap.open()

    def getFrame(self):
        ret, frame = self.cap.read()
        if ret:
            cv2.imshow("frame", frame)
            # time.sleep(1)
        return frame

    # 录制一段时长的
    def saveVideo(self, filepath, delays=600):
        # Define the codec and create VideoWriter object
        # 视频编码
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        outputPath = filepath
        # 30fps ,640*480size
        out = cv2.VideoWriter(outputPath, fourcc, 40.0, (640, 480))
        startTime = time.time()
        while (self.cap.isOpened):
            ret, frame = self.cap.read()
            if ret:
                # 翻转图片
                # frame = cv2.flip(frame,0)
                # write the flipped frame
                out.write(frame)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.cap.release()
                    break
            else:
                break
            if time.time() - startTime > delays:
                break
        out.release()
        cv2.destroyAllWindows()
        return True

    # 保存一个快照
    def saveSnapshot(self, filepath):
        if self.cap.isOpened:
            ret, frame = self.cap.read()
            if ret:
                cv2.imwrite(filepath, frame)
            else:
                print("save snapshot fail")
                return False
        return True

    def reOpen(self):
        if not self.cap.isOpened():
            print("re opened device")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.cap.open()
