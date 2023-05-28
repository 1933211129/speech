from NewTrain import get_feature
import tensorflow as tf
import numpy as np


model = tf.keras.models.load_model('emotion_recognition_model.h5')
audio_path = 'test1.wav'
audio_features = get_feature(audio_path)
audio_features_expanded = np.expand_dims(audio_features, axis=0)
predictions = model.predict(audio_features_expanded)
emotion_labels = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprised']
predicted_emotion = emotion_labels[np.argmax(predictions)]
print("预测结果:", predicted_emotion)
