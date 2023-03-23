from django.urls import path, re_path
from speach import views
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index),
    re_path(r'index/tip/(?P<tip>[^/]+)/$', views.index_tip),
    # path('speech_ai/', views.speech_ai),
    path('index/', views.index),
    path('test/', views.test),
    path('start_record/', views.start_record),
    path('stop_record/', views.stop_record),
    path('evaluation/', views.evaluation),
    path('index/result_visualization/', views.visualization),
    path('result_visualization/', views.visualization),

    path("upload/", views.upload_file),
    path("upload/TextAnalyse/", views.TextVisualizaton, name='TextVisualizaton'),
    #####################可视化测试###############################
    path('texterror/', views.TextVisualizaton),
    path('echarts_test/', views.echarts_visualization),
    path('table/', views.table),
    path('bar/', views.bar),
    path('radar/', views.radar_map_view),
    path('one_result/', views.one_result),
    
    path('flow_line/', views.line),
    path('flow_pie/', views.pie),
    path('line2/', views.line2),
    path('bar2/', views.bar2),
    path('bar1/', views.bar1),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
