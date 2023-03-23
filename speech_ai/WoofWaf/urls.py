from django.urls import path

from . import views

urlpatterns = [
    path('secure/login', views.secure_login),
    path('secure/index', views.secure_index),
    path('secure/ip_list', views.secure_ip_list),
    path('secure/ip_list/update', views.update_ip_list,name='WoofWaf-views-iplist_update' ),
    path('secure/ip_list/add', views.add_ip_list,name='WoofWaf-views-iplist_add' ),
    path('secure/temp_black_list', views.secure_temp_black_list),
    path('secure/defend_log', views.secure_defend_log),
    path('secure/trace_log', views.secure_trace_log),
    path('secure/pass_log', views.secure_pass_log),
    path('ParameterError', views.ParameterError),
    path('secure/HttpCheck', views.httpCheck),
    path('secure/HttpCheck/AddRule', views.httpCheckAddRule,name='WoofWaf-views-AddRule'),
    path('secure/HttpCheck/SetRule', views.httpCheckSetRule,name='WoofWaf-views-SetRule'),
    path('secure/HttpCheck/DelRule', views.httpCheckDelRule,name='WoofWaf-views-DelRule'),
    path('secure/HttpCheckSwitched', views.httpCheckSwitch, name='WoofWaf-views-Switch'),
    path('secure/UploadDefend', views.uploadDefend),
    path('secure/CCDefend', views.CCDefend),
    path('secure/waf_settings', views.settings),
    path('secure/waf_settings/sib', views.httpCheckSetIpBlock,name='WoofWaf-views-sib'),
]