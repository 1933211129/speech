from django.urls import path,re_path
from judge import views
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    # 视频打分
    path('video/', views.videoScore),
    path('humanScore/', views.HumanScore),

    # 视频提交
    path('submit/', views.submit),
    path('videoSubmit/', views.videoSubmit),

    # 赛事申请
    path('race/', views.RaceApplication),

    # 最终分数页面
    path('finalScore/', views.finalScore),


    # re_path(r'index/tip/(?P<tip>[^/]+)/$', views.index_tip),
    path('judge_homepage/', views.homepage),    # 赛事广场
    # path('judge_homepage/Competition_application/', views.my_form_view),  # 申请赛事，暂时不用
    path('judge_homepage/signup/', views.signup),   # 选手报名
    path('video/', views.video_index),    # 评委评分
    path('judge_homepage/contact/', views.contact),  # 联系我们
    path('judge_homepage/now/', views.show_events),  # 赛事广场——火热进行

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

