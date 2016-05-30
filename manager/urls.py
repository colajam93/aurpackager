from django.conf.urls import url
from manager import views

__PACKAGE_NAME_REGEX = r'(?P<package_name>[a-zA-Z0-9_+-]+)'

urlpatterns = [
    url(r'^$', views.package_list, name='package_list'),
    url(r'^packages/$', views.package_list, name='package_list'),
    url(r'^packages/register/$', views.package_register, name='package_register'),
    url(r'^packages/register/{}/$'.format(__PACKAGE_NAME_REGEX), views.package_register_detail,
        name='package_register_detail'),
    url(r'^packages/(?P<package_name>[a-zA-Z0-9_+-]+)/$', views.package_detail, name='package_detail'),
    url(r'^packages/(?P<package_name>[a-zA-Z0-9_+-]+)/(?P<build_number>\d+)/$', views.build_detail,
        name='build_detail'),
    url(r'^packages/(?P<package_name>[a-zA-Z0-9_+-]+)/(?P<build_number>\d+)/download/$', views.build_download,
        name='build_download'),
]
