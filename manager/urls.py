from django.conf.urls import url
from manager import views

urlpatterns = [
    url(r'^package/$', views.package_list, name='package_list'),
    url(r'^package/(?P<package_id>\d+)/$', views.package_detail, name='package_detail'),
    url(r'^build/(?P<build_id>\d+)/$', views.build_detail, name='build_detail')
]
