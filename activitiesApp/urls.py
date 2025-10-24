from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='home'),
    path('api/places/', views.places_geojson, name='places_geojson'),
    path('api/places/<int:pk>/', views.place_detail, name='place_detail'),
]
