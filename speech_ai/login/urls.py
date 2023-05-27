from django.urls import path, re_path
from login import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # 前端 测试
    path('temp', views.temp),

    # 登录注册
    path('', views.login_register),  # 登录注册
    path('login', views.login),  # 登录
    re_path(r'tip/(?P<tip>[^/]+)/$', views.login_tip),
    path('register', views.register),  # 注册
    path('logout', views.logout),  # 注销
    path('face/login', views.face_login),  # 人脸登录
    path('face/upload', views.face_upload),  # 人脸图片上传

    # 评估
    path('video', views.video),  # 上传视频
    path('speech', views.speech),  # 姿态表情分析

    # 用户个人界面
    path('upload/avatar', views.upload_avatar),
    path('show/avatar', views.show_avatar),
    path('user/info', views.user_info),

    # 得分
    path('score/', views.speachScore),
    re_path(r'score/(?P<date>[^/]+)/$', views.speachDateScore),
    # path('score/history_score', views.history_score),

    # 文本 需要完善
    re_path(r'txt/(?P<topic>[^/]+)/$',views.txt),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

