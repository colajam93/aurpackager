from django.conf.urls import url
from manager import views

urlpatterns = [
    url(r'^$', views.package_list, name='package_list'),
    url(r'^packages/(?P<package_name>[a-zA-Z0-9_+-]+)/$', views.package_detail, name='package_detail'),
    url(r'^packages/(?P<package_name>[a-zA-Z0-9_+-]+)/build/$', views.package_build, name='package_build'),
    url(r'^packages/(?P<package_name>[a-zA-Z0-9_+-]+)/(?P<build_number>\d+)/$', views.build_detail, name='build_detail')
]
