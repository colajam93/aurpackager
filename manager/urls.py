from django.conf.urls import url
from manager import views

_PACKAGE_NAME_REGEX = r'(?P<package_name>[a-zA-Z0-9_+-]+)'

urlpatterns = [
    url(r'^$', views.package_list, name='package_list'),
    url(r'^packages/$', views.package_list, name='package_list'),
    url(r'^packages/register/$', views.package_register, name='package_register'),
    url(r'^packages/register/{}/$'.format(_PACKAGE_NAME_REGEX), views.package_register_detail,
        name='package_register_detail'),
    url(r'^packages/{}/$'.format(_PACKAGE_NAME_REGEX), views.package_detail, name='package_detail'),
    url(r'^packages/{}/(?P<build_number>\d+)/$'.format(_PACKAGE_NAME_REGEX), views.build_detail,
        name='build_detail'),
    url(r'^packages/{}/(?P<build_number>\d+)/download/$'.format(_PACKAGE_NAME_REGEX), views.build_download,
        name='build_download'),
]
