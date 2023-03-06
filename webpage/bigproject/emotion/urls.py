from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('record/',views.record, name="record"),
    path('predict/',views.predict, name="predict"),
]