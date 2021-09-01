from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.pickStocks, name='stocks'),
    path('tracker', views.trackStocks, name='tracker')
]
