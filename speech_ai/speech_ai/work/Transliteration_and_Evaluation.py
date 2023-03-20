class trans_eval:
    def __init__(self, audiofile):
        self.audiofile = 'E:/django_ai/speech_ai/'+audiofile
        
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%get_token函数%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def get_token(cls):
        import base64
        import hashlib
        import hmac
        import requests
        import time
        import uuid
        from urllib import parse
        class AccessToken:
            @staticmethod
            def _encode_text(text):
                encoded_text = parse.quote_plus(text)
                return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
            @staticmethod
            def _encode_dict(dic):
                keys = dic.keys()
                dic_sorted = [(key, dic[key]) for key in sorted(keys)]
                encoded_text = parse.urlencode(dic_sorted)
                return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
            @staticmethod
            def create_token(access_key_id, access_key_secret):
                parameters = {'AccessKeyId': access_key_id,
                            'Action': 'CreateToken',
                            'Format': 'JSON',
                            'RegionId': 'cn-shanghai',
                            'SignatureMethod': 'HMAC-SHA1',
                            'SignatureNonce': str(uuid.uuid1()),
                            'SignatureVersion': '1.0',
                            'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            'Version': '2019-02-28'}
                # 构造规范化的请求字符串
                query_string = AccessToken._encode_dict(parameters)
                # print('规范化的请求字符串: %s' % query_string)
                # 构造待签名字符串
                string_to_sign = 'GET' + '&' + AccessToken._encode_text('/') + '&' + AccessToken._encode_text(query_string)
                # print('待签名的字符串: %s' % string_to_sign)
                # 计算签名
                secreted_string = hmac.new(bytes(access_key_secret + '&', encoding='utf-8'),
                                        bytes(string_to_sign, encoding='utf-8'),
                                        hashlib.sha1).digest()
                signature = base64.b64encode(secreted_string)
                # print('签名: %s' % signature)
                # 进行URL编码
                signature = AccessToken._encode_text(signature)
                # print('URL编码后的签名: %s' % signature)
                # 调用服务
                full_url = 'http://nls-meta.cn-shanghai.aliyuncs.com/?Signature=%s&%s' % (signature, query_string)
                # print('url: %s' % full_url)
                # 提交HTTP GET请求
                response = requests.get(full_url, verify=False)
                if response.ok:
                    root_obj = response.json()
                    key = 'Token'
                    if key in root_obj:
                        token = root_obj[key]['Id']
                        expire_time = root_obj[key]['ExpireTime']
                        return token, expire_time
                # print(response.text)
                return None, None
        # 用户信息
        access_key_id = 'LTAI5tDmPLjzT4yJ9xaNPu34'
        access_key_secret = '2rG2MD6hXanAdpeyOADtkLl2vLhbpv'
        token, expire_time = AccessToken.create_token(access_key_id, access_key_secret)
        return token
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%阿里云接口音频转写函数%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def ali_audio_rec(cls,audioFile, audioFileName, q):
        import http.client
        import json

        def process(request,  audioFile) :
            with open(audioFile, mode = 'rb') as f:
                audioContent = f.read()
            host = 'nls-gateway.cn-shanghai.aliyuncs.com'
            httpHeaders = {
                'Content-Length': len(audioContent)
                }
            conn = http.client.HTTPConnection(host)

            conn.request(method='POST', url=request, body=audioContent, headers=httpHeaders)
            response = conn.getresponse()
            print('Response status and response reason:')
            print(response.status ,response.reason)
            body = response.read()
            try:
                print('Recognize response is:')
                body = json.loads(body)
                # print(body)
                status = body['status']
                if status == 20000000 :
                    result = body['result']
                    print('Recognize result: ' + result)
                else :
                    print('Recognizer failed!')
            except ValueError:
                print('The response is not json format string')
            conn.close()
            return body

        appKey = 'PStE5j0aeBM2SRCO'
        token = cls.get_token()


        url = 'https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/FlashRecognizer'
        format = 'wav'
        sampleRate = 16000
        enablePunctuationPrediction  = True
        enableInverseTextNormalization = True
        enableVoiceDetection  = False

        request = url + '?appkey=' + appKey
        request = request + '&token=' + token
        request = request + '&format=' + format
        request = request + '&sample_rate=' + str(sampleRate)
        # print('Request: ' + request)
        result = process(request, audioFile)
        text = []
        tmp = result['flash_result']['sentences']
        for i in range(len(tmp)):
            text.append(tmp[i]['text'])
        content = ''.join(text)
        q.put((audioFileName, content))
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%获取音频时长%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def audio_duration(cls, obj):
        import wave
        with wave.open(obj.audiofile, 'rb') as wav_file:
            num_frames = wav_file.getnframes()
            frame_rate = wav_file.getframerate()
            duration = num_frames / frame_rate
            return duration
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%音频分割%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def segment(cls, obj):
        import os
        import subprocess

        # 获取音频持续时长
        duration = int(cls.audio_duration(obj))
        # 如果音频文件小于30s，则不用分割
        if duration <= 30:
            return obj.audiofile
        else:
            segment_time = 30
        file_name, file_ext = os.path.splitext(obj.audiofile)
        command = ["ffmpeg", "-i", obj.audiofile, "-f", "segment", "-segment_time", str(segment_time), "-y", "{}_%03d{}".format(file_name, file_ext)]
        subprocess.run(command)
        
        # 返回分割后的音频文件名字列表
        segment_files = []
        for i in range(1000):
            segment_file = "{}_{:03d}{}".format(file_name, i, file_ext)
            if os.path.exists(segment_file):
                segment_files.append(segment_file)
            else:
                break
        return segment_files
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%列表分割%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# 为了适配阿里云最高10路并发
# my_list由segment传入
    @classmethod
    def list_split(cls, my_list):
        new_list = []
        # 判断列表长度是否大于 10
        if len(my_list) > 10:
            # 使用切片进行分割
            for i in range(0, len(my_list), 10):
                sub_list = my_list[i:i+10]
                new_list.append(sub_list)
            return new_list
        else:
            new_list.append(my_list)
            return new_list

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%执行音频转写函数%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # llist由list_split传入
    @classmethod
    def execute_aliyun(cls, llist):
        import threading
        from queue import Queue

        result = {}
        threads = []
        q = Queue()
        for i in range(len(llist)):
            for j in range(len(llist[i])):
                t = threading.Thread(target=cls.ali_audio_rec, args=(llist[i][j], llist[i][j], q))
                threads.append(t)
                t.start()

        # Wait for all threads to finish executing
        for t in threads:
            t.join()

        # Add the return values of all threads to the result dictionary
        while not q.empty():
            audioFileName, transliterationResult = q.get()
            result[audioFileName] = transliterationResult
        return result
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%缀词分析%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def Affix(cls, obj):
        import jieba
        import pandas as pd

        # 第一次分割
        global segment_files
        segment_files = cls.segment(obj)

        # 第二次分割，变为二维列表
        new_list = cls.list_split(segment_files)

        # 开始转写
        global result_trans
        result_trans = cls.execute_aliyun(new_list)
        
        # 统计缀词文本
        all_words = ''.join(list(result_trans.values()))
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
        return affix_score
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%语音评测%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def evaluation(cls, txt, audio, q,xml_name):
        from builtins import Exception, str
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
        import time
        from datetime import datetime


        STATUS_FIRST_FRAME = 0  # 第一帧的标识
        STATUS_CONTINUE_FRAME = 1  # 中间帧标识
        STATUS_LAST_FRAME = 2  # 最后一帧的标识

        #  BusinessArgs参数常量
        SUB = "ise"
        ENT = "cn_vip"
        # 中文题型：read_syllable（单字朗读，汉语专有）read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)
        CATEGORY = "read_chapter"
        CHECK_TYPE = 'easy'
        GROUP = 'pupil'
        # 待评测文本 utf8 编码，需要加utf8bom 头
        TEXT = '\uFEFF' + txt
        # *****************************************************************************************直接从文件读取的方式*********************************************************************

        # TEXT = '\uFEFF' + open(txt, "r", encoding='utf-8').read()

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
                        # print(xml.decode("gbk"))
                        print('北京时间：',xml_name)
                        with open(xml_name, 'w') as f:
                            f.write(xml.decode("gbk"))


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
                            AudioFile=audio, Text=TEXT)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.close()
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        time2 = datetime.now()
        print(time2 - time1)
        q.put(xml_name)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%执行语音评测%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def execute_xfei(cls,obj):
        import random
        import threading
        import queue
        # 分割完成的列表


        global result_trans
        sample = list(result_trans.keys())

        if len(sample) == 1:
            k = 1
        elif len(sample) < 8 and len(sample) > 1:
            k = 2
        else:
            k = len(sample)//4

        # 随机采样1/4
        evaluation_list = random.sample(sample, k=k)
        # 取出对应的文本构成一个字典
        evaluation_dict = {}
        for i in range(len(evaluation_list)):
            tmp_dict = {}
            tmp_dict[evaluation_list[i]] = result_trans[evaluation_list[i]]
            evaluation_dict.update(tmp_dict)
        
        result_list = []
        q = queue.Queue()
        audio = list(evaluation_dict.keys())
        num_threads = len(audio)
        threads = []

        for i in range(num_threads):
            name = obj.audiofile[:-4]
            t = threading.Thread(target=cls.evaluation, args=(evaluation_dict[audio[i]],audio[i], q, name+str(i)+'.xml'))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        while not q.empty():
            result_list.append(q.get())
        # 返回xml文件名字列表    
        return result_list

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%取出xml文件的值%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def get_xml_score(cls, file):
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(file)
        root = tree.getroot()  # 找到树根
        for child_1 in root[0][0]:
            d = child_1.attrib  # 将总评分各参数放入字典d
        return d
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%写入数据库%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    @classmethod
    def to_mysql(cls,obj):
        import pymysql


        # 先调用缀词函数激活全局变量segment_files and result_trans
        affix_score = cls.Affix(obj)

        xml_list = cls.execute_xfei(obj)


        # 存储分数
        fc_list = []
        ic_list = []
        pc_list = []
        tc_list = []
        for i in range(len(xml_list)):
            tmp_xml = cls.get_xml_score(xml_list[i])
            print('检查error——tmp_xml',tmp_xml)
            fc_list.append(tmp_xml['fluency_score'])
            ic_list.append(tmp_xml['integrity_score'])
            pc_list.append(tmp_xml['phone_score'])
            tc_list.append(tmp_xml['tone_score'])
        fluency_score = round(sum(fc_list) / len(fc_list), 2)
        integrity_score = round(sum(ic_list) / len(ic_list), 2)
        phone_score = round(sum(pc_list) / len(pc_list), 2)
        tone_score = round(sum(tc_list) / len(pc_list), 2)
        total_score = round(fluency_score * 0.4 + integrity_score * 0.1 + 
                            affix_score * 0.2 + phone_score * 0.15 + tone_score * 0.15, 2)

# 连接数据库
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
        n = 0
        d = {}
        sql_insert = "insert into speech_score.speach_table values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        param = (
            primary_key, obj.audiofile[:-4], '均值',
            fluency_score,
            integrity_score, phone_score, tone_score, 89, affix_score, total_score, 90)
        cur.execute(sql_insert, param)
        n += 1

        # print(d)
        conn.commit()
        cur.close()  # 关闭游标
        conn.close()  # 关闭连接
        print("finish")
