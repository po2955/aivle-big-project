#from django.contrib import admin
from django.urls import path #,include
from . import views
from . import gps

appname = 'safe'
urlpatterns = [
    path('', views.main, name='main'),
    path('robo/',views.robo,name="robo"),
    path('car/', views.video_feed, name = 'video_feed'),
    path('sanitationWorker/',views.video_feed2,name="detect"),
    path('gps/',gps.get_post,name="gps"),
]