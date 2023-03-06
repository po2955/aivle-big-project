"""bigproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from board.views import base_views, notice_views
import common.views as common_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('safe.urls')),
    path('board/',include('board.urls')), # 이거랑
    path('board/', base_views.index, name='index'), # 해결 필요 : 어째서 둘 다 해야 작동하지?
    path('common/',include('common.urls')),
    path('common/profile',common_views.profile_view, name='profile'),
    path('dash/',include('dash.urls')),
    path('emotion/', include(('emotion.urls', 'emotion'), namespace='emotion')),
    path('board/<int:notice_id>/download', notice_views.FileDownloadView.as_view(), name="download"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)