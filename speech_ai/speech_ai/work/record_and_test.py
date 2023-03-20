import jieba
import pandas as pd
import requests
from builtins import Exception, str, bytes
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import ssl
from wsgiref.handlers import format_date_time
from time import mktime
import _thread as thread
import xml.etree.ElementTree as ET
import re
import pymysql
import threading
import time
import os
from speech_ai.work.record import Recorder

rec = Recorder()


class RT:
    # ***********************************录制音频**********************************************
    def audio_recording(self):
        rec.start()

    def stop_audio(self):
        rec.stop()

    # ***********************************测评***************************************************
    def test_speach():
        audio_path = name_time + '.wav'
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%转文字%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        txt_audio_path = audio_path
        lfasr_host = 'http://raasr.xfyun.cn/api'
        # 请求的接口名
        api_prepare = '/prepare'
        api_upload = '/upload'
        api_merge = '/merge'
        api_get_progress = '/getProgress'
        api_get_result = '/getResult'
        # 文件分片大小10M
        file_piece_sice = 10485760

        # ——————————————————转写可配置参数————————————————
        # 参数可在官网界面（https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html）查看，根据需求可自行在gene_params方法里添加修改
        # 转写类型
        lfasr_type = 0
        # 是否开启分词
        has_participle = 'false'
        has_seperate = 'true'
        # 多候选词个数
        max_alternatives = 0
        # 子用户标识
        suid = ''

        class SliceIdGenerator:
            """slice id生成器"""

            def __init__(self):
                self.__ch = 'aaaaaaaaa`'

            def getNextSliceId(self):
                ch = self.__ch
                j = len(ch) - 1
                while j >= 0:
                    cj = ch[j]
                    if cj != 'z':
                        ch = ch[:j] + chr(ord(cj) + 1) + ch[j + 1:]
                        break
                    else:
                        ch = ch[:j] + 'a' + ch[j + 1:]
                        j = j - 1
                self.__ch = ch
                return self.__ch

        class RequestApi(object):
            def __init__(self, appid, secret_key, upload_file_path):
                self.appid = appid
                self.secret_key = secret_key
                self.upload_file_path = upload_file_path

            # 根据不同的apiname生成不同的参数,本示例中未使用全部参数您可在官网(https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html)查看后选择适合业务场景的进行更换
            def gene_params(self, apiname, taskid=None, slice_id=None):
                appid = self.appid
                secret_key = self.secret_key
                upload_file_path = self.upload_file_path
                ts = str(int(time.time()))
                m2 = hashlib.md5()
                m2.update((appid + ts).encode('utf-8'))
                md5 = m2.hexdigest()
                md5 = bytes(md5, encoding='utf-8')
                # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
                signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
                signa = base64.b64encode(signa)
                signa = str(signa, 'utf-8')
                file_len = os.path.getsize(upload_file_path)
                file_name = os.path.basename(upload_file_path)
                param_dict = {}

                if apiname == api_prepare:
                    # slice_num是指分片数量，如果您使用的音频都是较短音频也可以不分片，直接将slice_num指定为1即可
                    slice_num = int(file_len / file_piece_sice) + (0 if (file_len % file_piece_sice == 0) else 1)
                    param_dict['app_id'] = appid
                    param_dict['signa'] = signa
                    param_dict['ts'] = ts
                    param_dict['file_len'] = str(file_len)
                    param_dict['file_name'] = file_name
                    param_dict['slice_num'] = str(slice_num)
                elif apiname == api_upload:
                    param_dict['app_id'] = appid
                    param_dict['signa'] = signa
                    param_dict['ts'] = ts
                    param_dict['task_id'] = taskid
                    param_dict['slice_id'] = slice_id
                elif apiname == api_merge:
                    param_dict['app_id'] = appid
                    param_dict['signa'] = signa
                    param_dict['ts'] = ts
                    param_dict['task_id'] = taskid
                    param_dict['file_name'] = file_name
                elif apiname == api_get_progress or apiname == api_get_result:
                    param_dict['app_id'] = appid
                    param_dict['signa'] = signa
                    param_dict['ts'] = ts
                    param_dict['task_id'] = taskid
                return param_dict

            # 请求和结果解析，结果中各个字段的含义可参考：https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html
            def gene_request(self, apiname, data, files=None, headers=None):
                response = requests.post(lfasr_host + apiname, data=data, files=files, headers=headers)
                result = json.loads(response.text)
                if result["ok"] == 0:
                    if apiname == '/getResult':
                        results = re.findall(r"\"onebest\":\"(.+?)\",", result['data'])
                        print(results)
                        with open("E:/Pythonfiles/py/AIwords/txt/txt_files/" + txt_audio_path[:-4] + ".txt", "wt",
                                  encoding='utf-8') as pf:
                            print(results, file=pf)
                        # with open("E:/Pythonfiles/py/AIwords/txt/txt_files/"+txt_audio_path[-23:-4]+".txt", "w") as f:
                        #     f.write(result['data'])

                    print("{} success:".format(apiname) + str(result))
                    return result
                else:
                    print("{} error:".format(apiname) + str(result))
                    exit(0)
                    return result

            # 预处理
            def prepare_request(self):
                return self.gene_request(apiname=api_prepare,
                                         data=self.gene_params(api_prepare))

            # 上传
            def upload_request(self, taskid, upload_file_path):
                file_object = open(upload_file_path, 'rb')
                try:
                    index = 1
                    sig = SliceIdGenerator()
                    while True:
                        content = file_object.read(file_piece_sice)
                        if not content or len(content) == 0:
                            break
                        files = {
                            "filename": self.gene_params(api_upload).get("slice_id"),
                            "content": content
                        }
                        response = self.gene_request(api_upload,
                                                     data=self.gene_params(api_upload, taskid=taskid,
                                                                           slice_id=sig.getNextSliceId()),
                                                     files=files)
                        if response.get('ok') != 0:
                            # 上传分片失败
                            print('upload slice fail, response: ' + str(response))
                            return False
                        print('upload slice ' + str(index) + ' success')
                        index += 1
                finally:
                    'file index:' + str(file_object.tell())
                    file_object.close()
                return True

            # 合并
            def merge_request(self, taskid):
                return self.gene_request(api_merge, data=self.gene_params(api_merge, taskid=taskid))

            # 获取进度
            def get_progress_request(self, taskid):
                return self.gene_request(api_get_progress, data=self.gene_params(api_get_progress, taskid=taskid))

            # 获取结果
            def get_result_request(self, taskid):
                return self.gene_request(api_get_result, data=self.gene_params(api_get_result, taskid=taskid))

            def all_api_request(self):
                # 1. 预处理
                pre_result = self.prepare_request()
                taskid = pre_result["data"]
                # 2 . 分片上传
                self.upload_request(taskid=taskid, upload_file_path=self.upload_file_path)
                # 3 . 文件合并
                self.merge_request(taskid=taskid)
                # 4 . 获取任务进度
                while True:
                    # 每隔20秒获取一次任务进度
                    progress = self.get_progress_request(taskid)
                    progress_dic = progress
                    if progress_dic['err_no'] != 0 and progress_dic['err_no'] != 26605:
                        print('task error: ' + progress_dic['failed'])
                        return
                    else:
                        data = progress_dic['data']
                        task_status = json.loads(data)
                        if task_status['status'] == 9:
                            print('task ' + taskid + ' finished')
                            break
                        print('The task ' + taskid + ' is in processing, task status: ' + str(data))

                    # 每次获取进度间隔20S
                    time.sleep(60)
                # 5 . 获取结果
                self.get_result_request(taskid=taskid)

        # 注意：如果出现requests模块报错："NoneType" object has no attribute 'read', 请尝试将requests模块更新到2.20.0或以上版本(本demo测试版本为2.20.0)
        # 输入讯飞开放平台的appid，secret_key和待转写的文件路径

        APP_ID = "fc8e1805"
        SECRET_KEY = "a8f97f1715ad0d6079c6f79924ceb271"
        file_path = txt_audio_path  # 在这里更改 音频文件路径 这里直接使用录音函数返回的path
        api = RequestApi(appid=APP_ID, secret_key=SECRET_KEY, upload_file_path=file_path)
        api.all_api_request()
        txt_path = "E:/Pythonfiles/py/AIwords/txt/txt_files/" + txt_audio_path[:-4] + ".txt"

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%缀词统计%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        affix_path = txt_path
        all_words = open(affix_path, encoding='utf-8').read()
        # all_words = open('D:/Pythonfiles/py/AIwords/txt/txt_files/2022-07-09-00-04-51.txt', encoding='utf-8').read()
        # 分词
        word_list = jieba.lcut(all_words)
        # word_list = list(word for word in words)
        # 使用pandas统计并降序排列
        df = pd.DataFrame(word_list, columns=['word'])
        result = pd.DataFrame(df.groupby(['word']).size().sort_values(ascending=False))  # 排序之后弄成dataframe
        result['word'] = result.index
        result.columns = ['cnt', 'word']
        result.index = range(len(result))

        affix_dict = dict(zip(result['word'], result['cnt']))  # 将两列构成字典
        affix_list = ['额', '呃', '厄', '嗯', '嗯嗯', '恩']  # 自定义缀词列表 可补充
        affix_deduction = 0  # 缀词部分扣分总和
        for i in range(len(affix_list)):
            if affix_list[i] in affix_dict.keys():
                affix_deduction = affix_deduction + affix_dict.get(affix_list[i])
                pass
            pass
        affix_score = 100 - affix_deduction

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%循环评测%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        STATUS_FIRST_FRAME = 0  # 第一帧的标识
        STATUS_CONTINUE_FRAME = 1  # 中间帧标识
        STATUS_LAST_FRAME = 2  # 最后一帧的标识

        #  BusinessArgs参数常量
        SUB = "ise"
        ENT = "cn_vip"
        # 中文题型：read_syllable（单字朗读，汉语专有）read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)
        CATEGORY = "read_chapter"
        # 待评测文本 utf8 编码，需要加utf8bom 头
        # TEXT = '\uFEFF' + "**********"
        # *****************************************************************************************直接从文件读取的方式*********************************************************************
        TEXT = '\uFEFF' + open(txt_path, "r", encoding='utf-8').read()

        class Ws_Param(object):
            # 初始化
            def __init__(self, APPID, APIKey, APISecret, AudioFile, Text):
                self.APPID = APPID
                self.APIKey = APIKey
                self.APISecret = APISecret
                self.AudioFile = AudioFile
                self.Text = Text

                # 公共参数(common)
                self.CommonArgs = {"app_id": self.APPID}
                # 业务参数(business)，更多个性化参数可在官网查看
                self.BusinessArgs = {"category": CATEGORY, "sub": SUB, "ent": ENT, "cmd": "ssb",
                                     "auf": "audio/L16;rate=16000",
                                     "aue": "raw", "text": self.Text, "ttp_skip": True, "aus": 1}

            # 生成url
            def create_url(self):
                # wws请求对Python版本有要求，py3.7可以正常访问，如果py版本请求wss不通，可以换成ws请求，或者更换py版本
                url = 'ws://ise-api.xfyun.cn/v2/open-ise'
                # 生成RFC1123格式的时间戳
                utcnow = datetime.now()
                date = format_date_time(mktime(utcnow.utctimetuple()))
                # utcnow = datetime.now()
                # date = str(mktime(utcnow.utctimetuple()))
                # date = datetime.datetime.utcfromtimestamp(1604473706)

                # 拼接字符串
                signature_origin = "host: " + "ise-api.xfyun.cn" + "\n"
                signature_origin += "date: " + date + "\n"
                signature_origin += "GET " + "/v2/open-ise " + "HTTP/1.1"
                # 进行hmac-sha256进行加密
                signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                         digestmod=hashlib.sha256).digest()
                signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

                authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                    self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
                authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
                # 将请求的鉴权参数组合为字典
                v = {
                    "authorization": authorization,
                    "date": date,
                    "host": "ise-api.xfyun.cn"
                }
                # 拼接鉴权参数，生成url
                url = url + '?' + urlencode(v)

                # 此处打印出建立连接时候的url,参考本demo的时候，比对相同参数时生成的url与自己代码生成的url是否一致
                print("date: ", date)
                print("v: ", v)
                print('websocket url :', url)
                return url

        # 收到websocket消息的处理
        def on_message(ws, message):
            try:
                code = json.loads(message)["code"]
                sid = json.loads(message)["sid"]
                if code != 0:
                    errMsg = json.loads(message)["message"]
                    print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

                else:
                    data = json.loads(message)["data"]
                    status = data["status"]
                    result = data["data"]
                    if (status == 2):
                        xml = base64.b64decode(result)
                        # python在windows上默认用gbk编码，print时需要做编码转换，mac等其他系统自行调整编码
                        print(xml.decode("gbk"))
                        # print("完成" + str(a[m]) + "个测评")
                        # *****************************************************************************************修改路径*******************************************************************
                        with open(name_time + '.xml', 'w') as f:
                            f.write(xml.decode("gbk"))

                        # print("内存地址为：",end=" ")
                        # print(id(xml))


            except Exception as e:
                print("receive msg,but parse exception:", e)

        # 收到websocket错误的处理
        def on_error(ws, error):
            print("### error:", error)

        # 收到websocket关闭的处理
        def on_close(ws):
            print("### closed ###")

        # 收到websocket连接建立的处理
        def on_open(ws):
            def run(*args):
                frameSize = 1280  # 每一帧的音频大小
                intervel = 0.04  # 发送音频间隔(单位:s)
                status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

                with open(wsParam.AudioFile, "rb") as fp:
                    while True:
                        buf = fp.read(frameSize)
                        # 文件结束
                        if not buf:
                            status = STATUS_LAST_FRAME
                        # 第一帧处理
                        # 发送第一帧音频，带business 参数
                        # appid 必须带上，只需第一帧发送
                        if status == STATUS_FIRST_FRAME:
                            d = {"common": wsParam.CommonArgs,
                                 "business": wsParam.BusinessArgs,
                                 "data": {"status": 0}}
                            d = json.dumps(d)
                            ws.send(d)
                            status = STATUS_CONTINUE_FRAME
                        # 中间帧处理
                        elif status == STATUS_CONTINUE_FRAME:
                            d = {"business": {"cmd": "auw", "aus": 2, "aue": "raw"},
                                 "data": {"status": 1, "data": str(base64.b64encode(buf).decode())}}
                            ws.send(json.dumps(d))
                        # 最后一帧处理
                        elif status == STATUS_LAST_FRAME:
                            d = {"business": {"cmd": "auw", "aus": 4, "aue": "raw"},
                                 "data": {"status": 2, "data": str(base64.b64encode(buf).decode())}}
                            ws.send(json.dumps(d))
                            time.sleep(1)
                            break
                        # 模拟音频采样间隔
                        time.sleep(intervel)
                # ws.close()

            thread.start_new_thread(run, ())

        # 测试时候在此处正确填写相关信息即可运行
        time1 = datetime.now()
        # APPID、APISecret、APIKey信息在控制台——语音评测了（流式版）——服务接口认证信息处即可获取
        wsParam = Ws_Param(APPID='fc8e1805', APISecret='MDljNTdkM2FmODFlN2MxYTFlYzU2YmYw',
                           APIKey='62f577753706bb60bf488b36822f6a0a',
                           AudioFile=audio_path, Text=TEXT)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.close()
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        time2 = datetime.now()
        print(time2 - time1)

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%写入数据库%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        import cv2
        import mediapipe as mp
        import numpy as np

        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_holistic = mp.solutions.holistic

        def med(success, image):
            with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
                if not success:
                    print("截取帧失败 !")
                    # If loading a video, use 'break' instead of 'continue'.
                    return np.array(0)

                # 原始图
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)

                # 渲染后的图
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # 识别脸部
                # mp_drawing.draw_landmarks(
                #     image,
                #     results.face_landmarks,
                #     mp_holistic.FACEMESH_CONTOURS,
                #     landmark_drawing_spec=None,
                #     connection_drawing_spec=mp_drawing_styles
                #     .get_default_face_mesh_contours_style())

                # 识别姿态
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles
                    .get_default_pose_landmarks_style())

                mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

                pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                                 results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.array(0)

                cv2.namedWindow("MediaPipe Holistic", 0)
                cv2.imshow('MediaPipe Holistic', image)  # cv2.flip(image, 1)

                # return lst
                if pose.any() == 0:
                    return np.array(0)
                return pose.reshape(-1, 4)

        # 求角度函数
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

            # 根据向量之间求其夹角并四舍五入
            Cobb = (np.arccos(x.dot(y) / (float(Lx * Ly))) * 180 / np.pi)

            return round(Cobb, 3)

        def Score(sta_data, test_data, scope):
            # 检验的部位
            lst = [11, 12]
            scores = []

            for test in test_data:
                max_score = 0
                for sta in sta_data:
                    score = 0
                    for key in lst:
                        angle = GetAngle(sta[key], sta[0], test[key], test[0])
                        if angle <= scope:
                            score += 1
                    if max_score < score:
                        max_score = score
                scores.append(max_score * 100 / len(lst))

            return scores

        # 视频截取、识别、得分
        # def main(seconds,out_path, input_video=0):
        def main(seconds, input_video=0):

            lst = []

            # print("视频截帧 start !")

            vidcap = cv2.VideoCapture(input_video)

            fps = vidcap.get(cv2.CAP_PROP_FPS)

            # print("每秒帧数: ", fps)

            if seconds == 0:
                fpsTime = 1
            else:
                fpsTime = fps * seconds

            # 开始帧
            startFps = 0

            if input_video == 0:
                flag = True
            else:
                flag = False

            vidcap.set(cv2.CAP_PROP_POS_FRAMES, startFps)
            success, image = vidcap.read()  # 获取第一帧
            count = 0  # 计数器 帧数

            if flag:
                while True:
                    if count % fpsTime == 0:
                        # 调用 med 函数 得到pose坐标
                        temp = med(success, image)
                        if temp.any() != 0:
                            lst.append(temp)

                    # 按 键盘上的 q 结束识别
                    if cv2.waitKey(1) & 0xff == ord('q'):
                        break
                    success, image = vidcap.read()
                    count += 1

            else:
                frametoStop = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
                while success and frametoStop >= count:
                    if count % fpsTime == 0:
                        # 调用 med 函数 得到pose坐标
                        temp = med(success, image)
                        if temp.any() != 0:
                            lst.append(temp)

                    # 按 键盘上的 q 结束识别
                    if cv2.waitKey(1) & 0xff == ord('q'):
                        break
                    success, image = vidcap.read()
                    count += 1

            # print('总帧数: ', count)

            # 释放资源
            vidcap.release()

            # 关闭展示窗口
            cv2.destroyAllWindows()

            return lst

        def sta(path):
            staList = []
            for i in os.listdir(path):
                img = cv2.imread(path + i)
                if img.any() == None:
                    flag = False
                else:
                    flag = True

                # img = cv2.imread("pic.jpg", cv2.IMREAD_COLOR)
                # img = cv2.imread("pic.jpg", cv2.IMREAD_GRAYSCALE)
                # img = cv2.imread("pic.jpg", cv2.IMREAD_UNCHANGED)

                # cv2.imshow("sta", img)
                staList.append(med(flag, img))

                # 等待按键 随意
                # cv2.waitKey(0)
                cv2.destroyAllWindows()

            return staList

        standard = sta('E:/django_ai/speech_ai/speech_ai/work/Standard_Action/')  # 标准动作路径
        print('标准动作总数：', len(standard))

        seconds = 0  # 隔几秒截帧    1：1秒识别一帧， 0：每一帧都识别
        input_video = 'E:/django_ai/speech_ai/' + name_time + '.mp4'  # 输入的视频路径

        # test = main(seconds) # 调用摄像头
        test = main(seconds, input_video)  # 调用视频，不使用摄像头

        print()
        scope = 20  # 允许的角度范围    20代表 左偏20度和右偏20度之内都可以
        arr = np.array(Score(standard, test, scope))  # 最终的分数   矩阵
        print('全部分数：', arr)
        print('样本量: {},  平均分: {:.2f},   方差: {:.3f}'.format(len(arr), arr.mean(), arr.std()))
        body_score = int(arr.mean())

        # 标准动作识别时，按任意键进行下一张图片的识别，视频和摄像头时，按 q 键 结束识别

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%写入数据库%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        conn = pymysql.connect(host='127.0.0.1',
                               user='root',
                               passwd='Kosm133164',
                               port=3306,
                               db='speech_score',
                               charset='utf8')

        cur = conn.cursor()  # 生成游标对象
        sql_select = "select*from speech_score.speach_table"  # 选择放入的table
        cur.execute(sql_select)
        primary_key = cur.execute(sql_select) + 10
        a = [x for x in range(1, 101)]
        n = 0
        d = {}
        tree = ET.parse(name_time + '.xml')
        root = tree.getroot()  # 找到树根
        for child_1 in root[0][0]:
            d = child_1.attrib  # 将总评分各参数放入字典d
        time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        total_score = round(
            float(d['fluency_score']) * 0.4 + float(d['integrity_score']) * 0.1 + affix_score * 0.2 + float(
                d['phone_score']) * 0.15 + float(d['tone_score']) * 0.15, 2)
        sql_insert = "insert into speech_score.speach_table values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        param = (
            primary_key, time_now, d['content'],
            round(float(d['fluency_score']), 2),
            round(float(d['integrity_score']), 2), round(float(d['phone_score']), 2), round(float(d['tone_score']), 2), 89, affix_score, total_score, body_score)
        cur.execute(sql_insert, param)
        n += 1

        # print(d)
        conn.commit()
        cur.close()  # 关闭游标
        conn.close()  # 关闭连接
        print("finish")
