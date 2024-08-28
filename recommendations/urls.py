# recommendations/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.jeju_intro, name='jeju_intro'),
    path('index/', views.index, name='index'),
    path('recommend/<str:category>/', views.recommend, name='recommend'),
    path('set_region/<str:region>/', views.set_jeju_region, name='set_jeju_region'),
        path('request-tts/', views.request_tts_view, name='request_tts'),  # TTS
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.TUTORIAL_URL, document_root=settings.TUTORIAL_ROOT)