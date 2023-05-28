import torch
from transformers import BertTokenizerFast, BertForSequenceClassification
import os
import wave
import os
import joblib
import numpy as np
import wave
from train import getFeature


class text_audio_emo_predict:
    def __init__(self, audio_name):
        self.audio_name = audio_name

    def text_predict(self, texts):
        '''文本预测'''
        # 设置使用的设备
        device = torch.device('cpu')

        # 初始化tokenizer和模型
        tokenizer = BertTokenizerFast.from_pretrained('E:/django_ai/speech_ai/login/py/EGG/bert-base-chinese')
        model = BertForSequenceClassification.from_pretrained("E:/code_test/text_model/ColabFiles", num_labels=3) # 修改为你的模型文件路径
        model.to(device)
        # 输入：一系列的文本
        # 输出：二维列表，每个子列表包含两个元素，第一个元素是预测结果，第二个元素是预测概率
        label_map = {0: "negative", 1: "neutral", 2: "positive"}
        encodings = tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**encodings)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            predictions = torch.argmax(logits, dim=-1)
        
        result = []
        for i in range(len(texts)):
            result.append([label_map[predictions[i].item()], probs[i][predictions[i]].item()])
        return result
    
    def audio_predict(self, audio_list):
        
        # 加载模型
        model = joblib.load("classfier.m")

        labels = np.array(['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'])
        emotion_label_list = []
        emotion_value_list = []

        for wav_path in audio_list:
            print(wav_path)
            f = wave.open(wav_path, 'rb')
            data_feature = getFeature(wav_path, 48)

            probability_data = model.predict_proba([data_feature])[0] # 获取概率列表
            max_probability_index = np.argmax(probability_data) # 最大概率的坐标
            max_probability = probability_data[max_probability_index] # 最大概率值
            emotion_label = labels[max_probability_index]  # 最终的表情
            emotion_label_list.append(emotion_label)
            emotion_value_list.append(max_probability)
            combined_list = [[emotion, value] for emotion, value in zip(emotion_label_list, emotion_value_list)]
            f.close()
        return combined_list

    def split_wav_file(self, segment_length=5):
        '''音频5s分割'''
        # 打开输入的 WAV 文件
        with wave.open(self.audio_name, 'rb') as wav_file:
            frame_rate = wav_file.getframerate()  # 采样率
            num_frames = wav_file.getnframes()  # 音频帧数
            channels = wav_file.getnchannels()  # 声道数
            bytes_per_sample = wav_file.getsampwidth()  # 每个采样的字节数

            segment_frames = segment_length * frame_rate  # 每个分割片段的帧数

            # 计算总的分割片段数
            total_segments = num_frames // segment_frames

            # 创建一个目录来存储分割后的音频文件
            output_dir = 'segmented_audio'
            os.makedirs(output_dir, exist_ok=True)

            segment_names = []

            # 将音频文件分割为片段
            for segment_index in range(total_segments):
                segment_start = segment_index * segment_frames
                segment_end = segment_start + segment_frames

                # 从输入的 WAV 文件中读取分割片段的帧
                wav_file.setpos(segment_start)
                segment_data = wav_file.readframes(segment_frames)

                # 创建一个新的 WAV 文件来存储分割片段
                segment_filename = f'{output_dir}/segment_{segment_index + 1}.wav'
                segment_names.append(segment_filename)

                with wave.open(segment_filename, 'wb') as segment_wav:
                    segment_wav.setnchannels(channels)
                    segment_wav.setsampwidth(bytes_per_sample)
                    segment_wav.setframerate(frame_rate)
                    segment_wav.writeframes(segment_data)
        return segment_names
    ###############################################列表分割#####################
    def list_split(self, my_list):
        new_list = []
        # 判断列表长度是否大于 10
        if len(my_list) > 10:
            # 使用切片进行分割
            for i in range(0, len(my_list), 10):
                sub_list = my_list[i:i + 10]
                new_list.append(sub_list)
            return new_list
        else:
            new_list.append(my_list)
            return new_list

    def get_token(self):
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
    ######################################转写测试函数###########################
    def ali_audio_rec(self, audioFiles):
        import threading
        import http.client
        import json
        
        def process(request, audioFile):
            with open(audioFile, mode='rb') as f:
                audioContent = f.read()
            host = 'nls-gateway.cn-shanghai.aliyuncs.com'
            httpHeaders = {
                'Content-Length': len(audioContent)
            }
            conn = http.client.HTTPConnection(host)
            conn.request(method='POST', url=request, body=audioContent, headers=httpHeaders)
            response = conn.getresponse()
            body = response.read()
            try:
                body = json.loads(body)
                status = body['status']
                if status == 20000000:
                    result = body['result']
                else:
                    print('Recognizer failed!')
            except ValueError:
                print('The response is not json format string')
            conn.close()
            return body

        def process_audio_file(audioFile, result_dict):
            request = url + '?appkey=' + appKey
            request = request + '&token=' + token
            request = request + '&format=' + format
            request = request + '&sample_rate=' + str(sampleRate)
            result = process(request, audioFile)
            try:
                text = []
                tmp = result['flash_result']['sentences']
                for i in range(len(tmp)):
                    text.append(tmp[i]['text'])
                content = ''.join(text)
                result_dict[audioFile] = content
                
            except KeyError:
                print(f"Warning: 'flash_result' key not found in result for file: {audioFile}")

        appKey = 'PStE5j0aeBM2SRCO'
        token = self.get_token()

        url = 'https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/FlashRecognizer'

        format = 'wav'
        sampleRate = 16000
        enablePunctuationPrediction = True
        enableInverseTextNormalization = True
        enableVoiceDetection = False

        threads = []
        result_dict = {}

        for audioFile in audioFiles:
            for audio in audioFile:
                thread = threading.Thread(target=process_audio_file, args=(audio, result_dict))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        return result_dict

    def total_predict(self):
        '''
        音频批量转写，音频文本预测，返回二元组
        第一个元素为音频预测二维列表
        第二个元素为文本预测二维列表
        '''
        # 按照5s分割的音频列表
        segment_names = self.split_wav_file()
        # 二次切分 多线程
        audio_files = self.list_split(segment_names)
        # 文本转写
        text_result_dict = self.ali_audio_rec(audio_files)
        # 按照顺序取出文本
        text_sorted_values = [value for _, value in sorted(text_result_dict.items())]
        # 文本评测存储概率值和label
        text_predict = self.text_predict(text_sorted_values)
        # 语音预测
        audio_predict = self.audio_predict(segment_names)
        return text_predict,audio_predict