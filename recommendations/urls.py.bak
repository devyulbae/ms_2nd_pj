# recommendations/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.jeju_intro, name='jeju_intro'),
    path('index/', views.index, name='index'),
    path('recommend/<str:category>/', views.recommend, name='recommend'),
    path('set_region/<str:region>/', views.set_jeju_region, name='set_jeju_region'),
]