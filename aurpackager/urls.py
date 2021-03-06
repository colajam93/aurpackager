"""aurpackager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

from aurpackager.settings import URL_PREFIX


def _application_directory():
    if URL_PREFIX:
        return URL_PREFIX.strip('/') + '/'
    else:
        return URL_PREFIX


urlpatterns = [
    url(r'^{}api/'.format(_application_directory()), include('api.urls', namespace='api')),
    url(r'^{}'.format(_application_directory()), include('manager.urls', namespace='manager'))
]
