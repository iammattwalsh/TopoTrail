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
    path('trail/<slug:slug>/get_trail_assets', views.get_trail_assets, name = 'get_trail_assets'),
    path('trail/<slug:slug>/get_user_trails', views.get_user_trails, name = 'get_user_trails'),
    path('trail/<slug:slug>/add_trail_photos', views.add_trail_photos, name = 'add_trail_photos'),
    path('trail/<slug:slug>/delete_trail_photo/<int:id>', views.delete_trail_photo, name = 'delete_trail_photo'),
    path('trail/<slug:slug>/edit_trail_photo/<int:id>', views.edit_trail_photo, name = 'edit_trail_photo'),
    path('trail/<slug:slug>/add_trail_comment', views.add_trail_comment, name = 'add_trail_comment'),
    path('trail/<slug:slug>/delete_trail_comment/<int:id>', views.delete_trail_comment, name = 'delete_trail_comment'),
    path('get_all_trails', views.get_all_trails, name = 'get_all_trails'),
]