import os
import librosa
import numpy as np
from tensorflow.keras.layers import Conv1D
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import MaxPooling1D, Flatten

from tensorflow.keras.layers import Input, Activation, multiply
from tensorflow.keras.models import Model

from tensorflow.keras import regularizers
from tensorflow.keras.layers import Dot, Activation
# 将情感标签转换为数字
EMOTION_LABEL = {
    'angry': 0,
    'fear': 1,
    'happy': 2,
    'neutral': 3,
    'sad': 4,
    'surprise': 5
}

def get_feature(path, n_mfcc=13, max_len=80):
    # 从音频文件中提取 MFCC 特征
    y, sr = librosa.load(path)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

    # 使用 StandardScaler 缩放 MFCC 特征
    scaler = StandardScaler()
    mfcc = scaler.fit_transform(mfcc.T).T

    if (max_len > mfcc.shape[1]):
        pad_width = max_len - mfcc.shape[1]
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :max_len]
    return np.squeeze(np.expand_dims(mfcc, axis=-1), axis=-1)


def get_data(n_mfcc=13, max_len=80):
    # 获取所有音频文件的 MFCC 特征和情感标签，并将 MFCC 特征转换为时间序列数据
    wav_file_path = []
    person_dirs = os.listdir('./casia')
    for person in person_dirs:
        if person.endswith('txt'):
            continue
        emotion_dir_path = os.path.join('./casia', person)
        emotion_dirs = os.listdir(emotion_dir_path)
        for emotion_dir in emotion_dirs:
            if emotion_dir.endswith('.ini'):
                continue
            emotion_file_path = os.path.join(emotion_dir_path, emotion_dir)
            emotion_files = os.listdir(emotion_file_path)
            for file in emotion_files:
                if not file.endswith('wav'):
                    continue
                wav_path = os.path.join(emotion_file_path, file)
                wav_file_path.append(wav_path)

    # 随机打乱音频文件
    np.random.shuffle(wav_file_path)

    data_feature = []
    data_labels = []

    for wav_file in wav_file_path:
        # 提取 MFCC 特征，并将其转换为时间序列数据
        mfcc = get_feature(wav_file, n_mfcc, max_len)
        data_feature.append(mfcc)
        data_labels.append(EMOTION_LABEL[wav_file.split('\\')[-2]])

    # 将情感标签转换为独热编码
    data_labels = to_categorical(data_labels)

    return np.array(data_feature), np.array(data_labels)


def build_model(n_mfcc=13, max_len=80, n_classes=6):
    # 构建模型
    model = Sequential()
    model.add(Conv1D(32, kernel_size=3, activation='relu', input_shape=(n_mfcc, max_len), kernel_regularizer=regularizers.l2(0.01)))
    model.add(LSTM(128, return_sequences=True, kernel_regularizer=regularizers.l2(0.01)))
    model.add(Dropout(0.5))
    model.add(LSTM(64, return_sequences=False, kernel_regularizer=regularizers.l2(0.01)))
    model.add(Dropout(0.5))
    model.add(Dense(n_classes, activation='softmax', kernel_regularizer=regularizers.l2(0.01)))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


if __name__ == '__main__':
    # 获取数据集
    X, y = get_data()
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # 构建模型
    model = build_model()
    # 训练模型
    model.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=32, epochs=50)
    # 评估模型准确率
    score = model.evaluate(X_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    # 保存模型
    model.save('LSTM_1D_CNN.h5')