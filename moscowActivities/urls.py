from django.contrib import admin
from rest_framework import routers
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
]
