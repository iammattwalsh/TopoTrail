from django.urls import path
from . import views

app_name = 'trails'
urlpatterns = [
    path('', views.home, name = 'home'),
    path('trail/<slug:slug>/processing', views.process_upload, name = 'process_upload'),
    path('trail/<slug:slug>', views.view_trail, name = 'view_trail'),
    path('new', views.new_trail, name = 'new_trail'),
    path('trail/<slug:slug>/edit', views.edit_trail, name = 'edit_trail'),
    path('trail/<slug:slug>/delete', views.delete_trail, name = 'delete_trail'),


    # path('test', views.vue_test, name = 'vue_test'),
    # path('test/<slug:slug>', views.vue_test_2, name = 'vue_test_2'),
]