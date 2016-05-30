from django.conf.urls import url
from manager import views

_PACKAGE_NAME_REGEX = r'(?P<package_name>[a-zA-Z0-9_+-]+)'
_BUILD_NUMBER_REGEX = r'(?P<build_number>\d+)'
_REGEX = {'name': _PACKAGE_NAME_REGEX, 'number': _BUILD_NUMBER_REGEX}

urlpatterns = [
    url(r'^$', views.package_list, name='package_list'),
    url(r'^packages/$', views.package_list, name='package_list'),
    url(r'^packages/register/$', views.package_register, name='package_register'),
    url(r'^packages/register/{name}/$'.format(**_REGEX), views.package_register_detail,
        name='package_register_detail'),
    url(r'^packages/{name}/$'.format(**_REGEX), views.package_detail, name='package_detail'),
    url(r'^packages/{name}/{number}/$'.format(**_REGEX), views.build_detail,
        name='build_detail'),
    url(r'^packages/{name}/{number}/download/$'.format(**_REGEX), views.build_download,
        name='build_download'),
]
