"""samplesite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url
from samplesite.views import hello_world,random_number,index,json_display,result,class_results,display_reval,display_allreval,after_reval
from samplesite.extraction import fetch_result
from django.conf.urls import include

urlpatterns = [
    path('',index),
    path('admin/', admin.site.urls),
    path('extract/',fetch_result),
    url(r'^classresults/(\w+)$',class_results),
    url(r'^student/(\w+)$',result),
    url(r'^student/(\w+)/new$',after_reval),
    url(r'^reval/(\w+)$',display_reval),
    url(r'^classreval/(\w+)$',display_allreval),
    path('json/',json_display)
]
