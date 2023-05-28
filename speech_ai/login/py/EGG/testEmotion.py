# import os
# from random import shuffle
# from train import getFeature
# from drawRadar import draw
# # from sklearn.externals import joblib
# import joblib
# import numpy as np
# import pyaudio
# import wave

# path = './casia'

# wav_paths = ['test1.wav']

# person_dirs = os.listdir(path)
# for person in person_dirs:
#     if person.endswith('txt'):
#         continue
#     emotion_dir_path = os.path.join(path, person)
#     emotion_dirs = os.listdir(emotion_dir_path)
#     for emotion_dir in emotion_dirs:
#         if emotion_dir.endswith('.ini'):
#             continue
#         emotion_file_path = os.path.join(emotion_dir_path, emotion_dir)
#         emotion_files = os.listdir(emotion_file_path)
#         for file in emotion_files:
#             if not file.endswith('wav'):
#                 continue
#             wav_path = os.path.join(emotion_file_path, file)
#             wav_paths.append(wav_path)

# # 将语音文件随机排列
# shuffle(wav_paths)

# model = joblib.load("classfier.m")

# p = pyaudio.PyAudio()
# for wav_path in wav_paths:
#     f = wave.open(wav_path, 'rb')
#     stream = p.open(
#         format=p.get_format_from_width(f.getsampwidth()),
#         channels=f.getnchannels(),
#         rate=f.getframerate(),
#         output=True)
#     data = f.readframes(f.getparams()[3])
#     stream.write(data)
#     stream.stop_stream()
#     stream.close()
#     f.close()
#     data_feature = getFeature(wav_path, 48)
#     print(model.predict([data_feature]))
#     print(model.predict_proba([data_feature]))
#     labels = np.array(['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'])

#     # draw(model.predict_proba([data_feature])[0], labels, 6)

# p.terminate()
# import os
# import joblib
# import numpy as np
# import pyaudio
# import wave

# from train import getFeature

# wav_path = 'test1.wav'  # 指定要预测情感的音频文件路径

# model = joblib.load("classfier.m")

# p = pyaudio.PyAudio()

# f = wave.open(wav_path, 'rb')
# stream = p.open(
#     format=p.get_format_from_width(f.getsampwidth()),
#     channels=f.getnchannels(),
#     rate=f.getframerate(),
#     output=True)
# data = f.readframes(f.getparams()[3])
# stream.write(data)
# stream.stop_stream()
# stream.close()
# f.close()

# data_feature = getFeature(wav_path, 48)
# labels = np.array(['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'])

# prediction = model.predict([data_feature])[0]
# emotion_label = labels[prediction]
# print(emotion_label)

# p.terminate()
# import os
# import joblib
# import numpy as np
# import wave

# from train import getFeature

# wav_path = 'test1.wav'  # 指定要预测情感的音频文件路径

# model = joblib.load("classfier.m")

# f = wave.open(wav_path, 'rb')
# data_feature = getFeature(wav_path, 48)
# labels = np.array(['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'])

# prediction = model.predict([data_feature])[0]
# emotion_label = labels[prediction]
# print(emotion_label)

# f.close()
# import os
# import joblib
# import numpy as np
# import wave

# from train import getFeature

# wav_paths = ['test1.wav', 'test2.wav', 'test3.wav', 'test4.wav', 'test5.wav']  # 指定要预测情感的音频文件路径列表
# model = joblib.load("classfier.m")

# labels = np.array(['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'])
# emotion_results = []

# for wav_path in wav_paths:
#     f = wave.open(wav_path, 'rb')
#     data_feature = getFeature(wav_path, 48)

#     prediction = model.predict([data_feature])[0]
#     emotion_label = labels[prediction]
#     emotion_results.append(emotion_label)

#     f.close()

# print(emotion_results)

import os
import joblib
import numpy as np
import wave

from train import getFeature

wav_paths = ['E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_1.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_10.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_11.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_12.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_13.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_14.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_2.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_3.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_4.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_5.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_6.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_7.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_8.wav',
 'E:\\django_ai\\speech_ai\\login\\py\\EGG\\segmented_audio\\segment_9.wav']
model = joblib.load("classfier.m")

labels = np.array(['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise'])
emotion_label_list = []
emotion_value_list = []

for wav_path in wav_paths:
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

print(combined_list)
