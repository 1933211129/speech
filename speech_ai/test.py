#!/usr/bin/env python
# -*- coding: utf-8 -*-
def get_token():
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
    access_key_id = 'XXXXXXXXXX'
    access_key_secret = 'XXXXXXXX'
    token, expire_time = AccessToken.create_token(access_key_id, access_key_secret)
    return token


def list_split(my_list):
    new_list = []
    # 判断列表长度是否大于 8
    if len(my_list) > 8:
        # 使用切片进行分割
        for i in range(0, len(my_list), 8):
            sub_list = my_list[i:i+8]
            new_list.append(sub_list)
        return new_list
    else:
        new_list.append(my_list)
        return new_list


def ali_audio_rec(audioFile,q):
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
    token = get_token()


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
    result = process(request, audioFile)
    text = []
    tmp = result['flash_result']['sentences']
    for i in range(len(tmp)):
        text.append(tmp[i]['text'])
    content = ''.join(text)
    result_dict.update({audioFile: content})
    q.put(result_dict)




import threading
from queue import Queue


llist = ['2022-09-12-15-37-00_000.wav',
 '2022-09-12-15-37-00_001.wav',
 '2022-09-12-15-37-00_002.wav',
 '2022-09-12-15-37-00_003.wav',
 '2022-09-12-15-37-00_004.wav',
 '2022-09-12-15-37-00_005.wav',
 '2022-09-12-15-37-00_006.wav',
 '2022-09-12-15-37-00_007.wav',
 '2022-09-12-15-37-00_008.wav',
 '2022-09-12-15-37-00_009.wav',
 '2022-09-12-15-37-00_010.wav']

split_list = list_split(llist)
result_dict = {}

for i in range(len(split_list)):
    q = Queue()
    threads = []
    for j in range(len(split_list[i])):
        t = threading.Thread(target=ali_audio_rec, args=(split_list[i][j], q))
        threads.append(t)
        t.start()

# 等待所有线程执行完毕
for t in threads:
    t.join()

# 将所有线程的返回值加入结果字典中，音频文件名字作为字典的键，识别结果作为字典的值
while not q.empty():
    audio_file_name = split_list[i][q.qsize() - 1]
    result_dict[audio_file_name] = q.get(split_list[i][j])
print(result_dict)
