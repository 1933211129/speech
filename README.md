## 项目基本信息

基于人工智能的演讲评分系统</br>
speech system base on AI</br>
2023年中国大学生计算机设计大赛(4C)——人工智能应用——人工智能实践赛作品</br>
作品编号：2023015586</br>

## 项目简介

本项目基于B/S架构设计开发了一款基于人工智能的演讲评分系统。在多维度数据采集的基础上，利用智能语音技术，对演讲者语音的流畅度、清晰度和发音准确度等进行评测；运用文本分析技术，分析和评测演讲者演讲稿的写作质量；采用人体姿态评估技术分析演讲者的演讲姿态、面部表情评判演讲者的肢体动作和表情是否得体。根据不同角度的评判标准，最终量化为具体的评分；同时，考虑到评测系统的安全性，从防护SQL注入、治理流量攻击、存储防御日志等多途径实现信息安全防护。



## 项目运行

### 项目配置

下载weights.zip，解压缩后，放到media目录下，例如 `speech_ai/media/weights`

下载casia.zip，解压缩后，放到login/py/EGG下，例如`speech_ai/login/py/EGG/casia`

下载fmpeg.zip，解压缩后，配置环境变量，例如`C:\Users\gongz\Desktop\ffmpeg\bin`


安装mysql数据库，连接数据库，新建`speech_score`数据库，并修改项目文件夹 `speech_ai/speech_ai/setting.py`，需要修改的代码如下
```

DATABASES = {  
	'default': {  
	'ENGINE': 'django.db.backends.mysql',  
	'NAME': 'speech_score', # 数据库名
	'USER': 'root',  
	'PASSWORD': '123456', # 更改成自己的数据密码
	'HOST': '127.0.0.1',  
	'PORT': 3306,  
	}  
}


```

### 环境

```powershell

# 创建环境
conda create -n speech python=3.7

# 激活环境
conda activate speech

# 设置pip源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 命令行下，进入项目文件夹根目录，例如 `cd C:\Users\gongz\Desktop\speech_ai`
pip install -r requirements.txt


```

### 运行

```powershell
# 启动数据库

# 命令行下，进入项目文件夹根目录，例如
cd C:\Users\gongz\Desktop\speech_ai

# 数据库表迁移
python manage.py makemigrations
python manage.py migrate

# 运行
python .\manage.py runserver

```
