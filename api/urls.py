from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^search/$', views.package_search, name='package_search'),
    url(r'^info/$', views.package_info, name='package_info'),
    url(r'^register/$', views.package_register, name='package_register'),
    url(r'^remove/$', views.package_remove, name='package_remove'),
]
