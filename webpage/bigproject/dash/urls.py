from django.urls import path
from . import views

app_name = 'dash'
urlpatterns = [
    path('', views.mainboard, name='main'),
    path('<str:dist_id>', views.district, name='district'),
    path('alertalarm/',views.alertalarm, name='alertalarm'),
    path('company_table/<str:dist_id>', views.company_table, name='company_table'),
    path('alarm_table/<str:dist_id>', views.alarm_table, name='alarm_table'),
    path('accident_table/<str:dist_id>', views.accident_table, name='accident_table'),
    path('status_table/<str:dist_id>', views.status_table, name='status_table'),
    #path('acc_create/', views.acc_create, name='acc_create'),
]