from django.urls import path

from . import views

urlpatterns = [
    path('waf/login', views.login_waf,name='WoofWaf-views-login'),
    path('waf/logout', views.logout_waf,name='WoofWaf-views-logout'),
    path('secure/index', views.secure_index,name='WoofWaf-views-index'),
    path('secure/ip_list', views.secure_ip_list,name='WoofWaf-views-ip_list'),
    path('secure/ip_list/update', views.update_ip_list,name='WoofWaf-views-iplist_update' ),
    path('secure/ip_list/add', views.add_ip_list,name='WoofWaf-views-iplist_add' ),
    path('secure/temp_black_list', views.secure_temp_black_list,name='WoofWaf-views-tbl'),
    path('secure/defend_log', views.secure_defend_log,name='WoofWaf-views-defend_log'),
    path('secure/trace_log', views.secure_trace_log,name='WoofWaf-views-trace_log'),
    path('secure/pass_log', views.secure_pass_log,name='WoofWaf-views-pass_log'),
    path('ParameterError', views.ParameterError,name='Woof-ParameterError'),
    path('secure/HttpCheck', views.httpCheck,name='WoofWaf-views-HttpCheck'),
    path('secure/HttpCheck/AddRule', views.httpCheckAddRule,name='WoofWaf-views-AddRule'),
    path('secure/HttpCheck/SetRule', views.httpCheckSetRule,name='WoofWaf-views-SetRule'),
    path('secure/HttpCheck/DelRule', views.httpCheckDelRule,name='WoofWaf-views-DelRule'),
    path('secure/HttpCheckSwitched', views.httpCheckSwitch, name='WoofWaf-views-Switch'),
    path('secure/ccSwitch', views.ccSwitch, name='WoofWaf-views-ccSwitch'),
    path('secure/UploadDefend', views.uploadDefend,name='WoofWaf-views-upload'),
    path('secure/CCDefend', views.CCDefend,name='WoofWaf-views-CCDefend'),
    path('secure/waf_settings', views.settings,name='WoofWaf-views-settings'),
    path('secure/waf_settings/sib', views.httpCheckSetIpBlock,name='WoofWaf-views-sib'),
]