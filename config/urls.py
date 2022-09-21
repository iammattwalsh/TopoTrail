"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

# from . import views

handler404 = 'config.views.page_not_found_view'
handler500 = 'config.views.error_view'
handler403 = 'config.views.permission_denied_view'
handler400 = 'config.views.bad_request_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path('', include('trails.urls')),
    re_path(r'^uploads/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # path('errortest', views.errortest)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
