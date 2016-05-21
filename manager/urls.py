from django.conf.urls import url
from manager import views

urlpatterns = [
    url(r'^$', views.package_list, name='package_list'),
    url(r'^(?P<package_id>\d+)/$', views.package_detail, name='package_detail'),
    url(r'^(?P<package_id>\d+)/build/$', views.package_build, name='package_build'),
    url(r'^(?P<package_id>\d+)/(?P<build_number>\d+)/$', views.build_detail, name='build_detail')
]
