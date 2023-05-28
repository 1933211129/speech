# from concurrent.futures import ThreadPoolExecutor
# from NewTrain import get_feature
# import tensorflow as tf
# import numpy as np
# import concurrent.futures
# import os
# import time

# start_time = time.time()
# dir_path = 'E:/code_test/音频/EGG/audio/'
# # 获取该路径下所有文件名
# file_names = os.listdir(dir_path)
# # 构建绝对路径列表
# abs_file_paths = [os.path.join(dir_path, file_name) for file_name in file_names if file_name.endswith('.wav')]

# model = tf.keras.models.load_model('emotion_recognition_model.h5')
# emotion_labels = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprised']

# audio_files = abs_file_paths  # 示例音频文件列表

# def predict_emotion(audio_file):
#     audio_features = get_feature(audio_file)
#     audio_features_expanded = np.expand_dims(audio_features, axis=0)
#     predictions = model.predict(audio_features_expanded)
#     predicted_emotion = emotion_labels[np.argmax(predictions)]
#     return predicted_emotion

# predicted_emotions = {}

# with ThreadPoolExecutor(max_workers=len(audio_files)) as executor:
#     future_to_file = {executor.submit(predict_emotion, audio_file): audio_file for audio_file in audio_files}
#     for future in concurrent.futures.as_completed(future_to_file):
#         audio_file = future_to_file[future]
#         try:
#             predicted_emotions[audio_file] = future.result()
#         except Exception as e:
#             print(f"音频文件 {audio_file} 预测时出错: {e}")

# end_time = time.time()
# print(predicted_emotions)
# print("用时：", end_time - start_time)

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from NewTrain import get_feature
import tensorflow as tf
import numpy as np
import concurrent.futures
import os
import time

start_time = time.time()
dir_path = 'E:/code_test/音频/EGG/audio/'
file_names = os.listdir(dir_path)
abs_file_paths = [os.path.join(dir_path, file_name) for file_name in file_names if file_name.endswith('.wav')]

model = tf.keras.models.load_model('emotion_recognition_model.h5')
emotion_labels = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprised']

audio_files = abs_file_paths

def predict_emotion(audio_file):
    audio_features = get_feature(audio_file)
    audio_features_expanded = np.expand_dims(audio_features, axis=0)
    predictions = model.predict(audio_features_expanded)
    predicted_emotion = emotion_labels[np.argmax(predictions)]
    return predicted_emotion

predicted_emotions = {}

# 将模型保存为 SavedModel 格式
saved_model_path = "saved_model"
model.save(saved_model_path)

def predict_emotion_process(audio_file):
    # 在每个进程中重新加载模型
    model = tf.keras.models.load_model(saved_model_path)
    return predict_emotion(audio_file)

max_workers = 8  # 根据你的计算机配置来设置合适的值

# 使用 ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=max_workers) as executor:
    future_to_file = {executor.submit(predict_emotion_process, audio_file): audio_file for audio_file in audio_files}
    for future in concurrent.futures.as_completed(future_to_file):
        audio_file = future_to_file[future]
        try:
            predicted_emotions[audio_file] = future.result()
        except Exception as e:
            print(f"音频文件 {audio_file} 预测时出错: {e}")

# 使用 ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_file = {executor.submit(predict_emotion, audio_file): audio_file for audio_file in audio_files}
    for future in concurrent.futures.as_completed(future_to_file):
        audio_file = future_to_file[future]
        try:
            predicted_emotions[audio_file] = future.result()
        except Exception as e:
            print(f"音频文件 {audio_file} 预测时出错: {e}")

end_time = time.time()
print(predicted_emotions)
print("用时：", end_time - start_time)
