from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^search/$', views.package_search, name='package_search'),
    url(r'^info/$', views.package_info, name='package_info'),
    url(r'^register/$', views.package_register, name='package_register'),
    url(r'^remove/$', views.package_remove, name='package_remove'),
    url(r'^remove_build/$', views.remove_build, name='remove_build'),
    url(r'^cleanup/$', views.cleanup, name='cleanup'),
    url(r'^cleanup_all/$', views.cleanup_all, name='cleanup_all'),
    url(r'^build/$', views.package_build, name='package_build'),
    url(r'^build_all/$', views.package_build_all, name='package_build_all'),
    url(r'^install/$', views.package_install, name='package_install'),
    url(r'^toggle_ignore/$', views.toggle_ignore, name='toggle_ignore'),
]
