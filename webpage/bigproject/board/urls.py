from django.urls import path
from .views import base_views, notice_views, reply_views

app_name = 'board'
urlpatterns=[
    #base_views
    path('', base_views.index, name='index'),
    path('<int:notice_id>/', base_views.detail, name='detail'),
    
    #notice_views
    path('notice/create/', notice_views.notice_create, name='notice_create'),
    #NoticeCreateView
    path('notice/modify/<int:notice_id>/', notice_views.notice_modify, name='notice_modify'),
    path('notice/delete/<int:notice_id>/', notice_views.notice_delete, name='notice_delete'),
    
    #reply_views
    path('notice/create/<int:notice_id>', reply_views.reply_create, name='reply_create'),
    path('reply/modify/<int:reply_id>/', reply_views.reply_modify, name='reply_modify'),
    path('reply/delete/<int:reply_id>/', reply_views.reply_delete, name='reply_delete'),
]
