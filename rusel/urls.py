"""rusel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from . import views

urlpatterns = i18n_patterns(
    path('',          views.index,    name='index'),
    path('feedback/', views.feedback, name='feedback'),
    path('trip/',     include('trip.urls')),
    path('fuel/',     include('fuel.urls')),
    path('apart/',    include('apart.urls')),
    path('proj/',     include('proj.urls')),
    path('task/',     include('task.urls')),
    path('note/',     include('note.urls')),
    path('pir/',      include('pir.urls')),
    path('store/',    include('store.urls')),
    path('wage/',     include('wage.urls')),
    path('account/',  include('account.urls')),
    path('admin/',    admin.site.urls, name='admin'),
)
