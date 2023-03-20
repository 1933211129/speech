import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
from .feature_extractor import FeatureExtractor


def train():
    df = pd.read_csv('./data/sqli_test.csv')
    fe = FeatureExtractor()
    # 将原数据集转化为带有特征标签的数据集
    fedf = fe.transform(df)

    fedf.dropna(inplace=True)
    fedf.drop_duplicates(inplace=True)
    fedf.reset_index(inplace=True, drop=True)

    # 分离特征和标签
    X = df.drop("label", axis=1)
    y = df["label"]
    # 划分集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=41)
    # 模型
    model = RandomForestClassifier(n_estimators=100, random_state=41)
    # 训练
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("Accuracy: ", acc)


def payload_predict(payload:str):
    model_path = 'WoofWaf/payload_ai/model.joblib'
    model = joblib.load(model_path)
    fe = FeatureExtractor()
    new_data = FeatureExtractor.payload_transform(fe, payload)
    # 预测
    prediction = model.predict(new_data)
    if prediction[0]==1.0:
        # 攻击
        return True
    else:return False

if __name__ =='__main__':
    # train()
    payload='"1"" and 6537  =  dbms_pipe.receive_message  (  chr  (  76  )  ||chr  (  116  )  ||chr  (  117  )  ||chr  (  65  )  ,5  )  "'
    print(payload_predict(payload))