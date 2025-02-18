from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.static import serve

from Park.settings import MEDIA_ROOT, MEDIA_URL
from app import views

# 主路由
urlpatterns = [   #这个是后台自带的管理系统，我们不用管他
                  path('admin/', admin.site.urls),  # 后台管理系统
                  path('', views.login),  # 登录，空的就登录
                  path('login/', views.login),  # 登录
                  path('logout/', views.logout),  # 退出登录
                  path('index/', views.index),  # 首页
                  path('user_info/', views.user_info),
                  path('user_add/', views.user_add),
                  path('user_del/', views.user_del),
                  path('user_edit/', views.user_edit),
                  path('user_renewal/', views.user_renewal),
                  path('user_paging/', views.user_paging),
                  path('car_port_pagingA/', views.car_port_pagingA),
                  path('car_port_pagingB/', views.car_port_pagingB),
                  path('car_port_pagingC/', views.car_port_pagingC),
                  path('car_port_pagingD/', views.car_port_pagingD),
                  path('car_record_paging/', views.car_record_paging),
                  path('car_import/', views.car_import),
                  path('test/', views.test),
                  path('test2/', views.test2),
                  path('pay/', views.pay),
                  path('code/', views.code),
                  path('car_exit/', views.car_exit),
                  path('car_port/', views.car_port),
                  path('car_record/', views.car_record),
                  path('car_port_info/<str:id>/', views.car_port_info),
                  path(r'media/(?P<path>.*)/', serve, {'document_root': MEDIA_ROOT}),
                  path('carPark_position/', views.carPark_position),
                  path('carPark_count/', views.carPark_count),
                  path('video/', views.video),
                  path('pretest/', views.pretest),
                  path('api/table-data/', views.get_table_data, name='table-data'),

              ] + static(MEDIA_URL, document_root=MEDIA_ROOT)
