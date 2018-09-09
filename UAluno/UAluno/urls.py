"""UAluno URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
import django.contrib.auth.views
from datetime import datetime

import app.forms
import app.views
from django.contrib import admin

urlpatterns = [
    url(r'^$', app.views.home, name="home"),
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^ementas/(day=(?P<day>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday))?$', app.views.ementas, name="ementas"),
    url(r'^noticias/(filter=(?P<filter>[0-9]+))?$', app.views.noticias, name="noticias"),
    url(r'^metereologia/(day=(?P<day>[0-6]))?$', app.views.metereologia, name="metereologia"),
    url(r'^registar/$', app.views.registar, name="registar"),
    url(r'^notas/(status=(?P<status>(success|error)))?$', app.views.notas, name="notas"),
    url(r'^remove_course/', app.views.remove_course, name="remove_course"),
    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html',
            'extra_context':
            {
                'title': 'Entrar com a sua conta',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),
    url(r'^send/$', app.views.send_message),
]
