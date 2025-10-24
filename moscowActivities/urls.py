from django.contrib import admin
from rest_framework import routers
from django.shortcuts import render
from django.urls import path

def map_view(request):
    return render(request, 'index.html')


urlpatterns = [
    path("", map_view, name="home"),
    path('admin/', admin.site.urls),
]
