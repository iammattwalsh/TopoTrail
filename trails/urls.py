from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('processing/<slug:slug>', views.process_upload, name = 'process_upload'),
    # path('test', views.test, name = 'test'), # test to make sure initiated code will continue to run after page close
]