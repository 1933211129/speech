## Basic Project Information

AI-based Speech Scoring System</br>
speech system base on AI</br>
2023 China University Computer Design Competition (4C) — AI Application — AI Practice Competition — National First Prize — Featured Work</br>
Work ID: 2023015586</br>

## Project Introduction

This project is an AI-based speech scoring system developed using a B/S architecture. Based on multi-dimensional data collection, it utilizes intelligent speech technology to evaluate the fluency, clarity, and pronunciation accuracy of the speaker's voice; employs text analysis technology to analyze and evaluate the writing quality of the speech script; and adopts human pose estimation technology to analyze the speaker's posture and facial expressions to judge whether their body language and expressions are appropriate. Based on judgment criteria from different perspectives, the final results are quantified into specific scores. Additionally, considering the security of the evaluation system, information security protection is implemented through multiple methods, including defending against SQL injection, managing traffic attacks, and storing defensive logs.

## Project Operation

### Configuration

Download `weights.zip`, unzip it, and place it in the `media` directory. File structure: `speech_ai/media/weights`

Download `casia.zip`, unzip it, and place it in the `login/py/EGG` directory. File structure: `speech_ai/login/py/EGG/casia`

Download `fmpeg.zip`, unzip it, and configure the environment variables, for example: `C:\Users\gongz\Desktop\ffmpeg\bin`


Install the MySQL database, connect to the database, create a new `speech_score` database, and modify the project folder `speech_ai/speech_ai/setting.py`. The code to be modified is as follows:
```
DATABASES = {  
	'default': {  
	'ENGINE': 'django.db.backends.mysql',  
	'NAME': 'speech_score', # Database name
	'USER': 'root',  
	'PASSWORD': '123456', # Change to your own database password
	'HOST': '127.0.0.1',  
	'PORT': 3306,  
	}  
}
```

### Environment

```powershell
# Create environment
conda create -n speech python=3.7

# Activate environment
conda activate speech

# Set pip source
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Install necessary python packages
pip install -r requirements.txt
```

### Running

```powershell
# Start database
# In the command line, enter the project root directory, for example:
cd C:\Users\gongz\Desktop\speech_ai

# Database table creation
python manage.py makemigrations
python manage.py migrate

# Run
python .\manage.py runserver
```
