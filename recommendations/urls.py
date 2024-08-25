# recommendations/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recommend/<str:category>/', views.recommend, name='recommend'),
]