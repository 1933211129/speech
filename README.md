# 项目基本信息
基于人工智能的演讲评分系统</br>
speech system base on AI</br>
2023年中国大学生计算机设计大赛(4C)——人工智能应用——人工智能实践赛作品</br>
作品编号：2023015586</br>
# 项目简介
本项目基于B/S架构设计开发了一款基于人工智能的演讲评分系统。在多维度数据采集的基础上，利用智能语音技术，对演讲者语音的流畅度、清晰度和发音准确度等进行评测；运用文本分析技术，分析和评测演讲者演讲稿的写作质量；采用人体姿态评估技术分析演讲者的演讲姿态、面部表情评判演讲者的肢体动作和表情是否得体。根据不同角度的评判标准，最终量化为具体的评分；同时，考虑到评测系统的安全性，从防护SQL注入、治理流量攻击、存储防御日志等多途径实现信息安全防护。

# 项目拉取

```shell
git clone https://github.com/1933211129/speech.git
```

# 项目运行

## 项目运行环境

`Windows10、Windows11、macOS Monterey（12.0）`

`Pycharm or VScode`

`MySQL8.0`

`python3.x && requirements.txt`

## 项目运行

cd到项目`speech_ai`文件夹下

`数据库迁移`

```shell
python manage.py makemigrations
python manage.py migrate
```

`启动服务器`

```
python .\manage.py runserver
```

