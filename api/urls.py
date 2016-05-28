from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^search/$', views.package_search, name='package_search'),
]
