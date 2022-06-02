from django.contrib import admin
from .models import Trail, Waypoint, Photo, Comment, Rating

admin.site.register(Trail)
admin.site.register(Waypoint)
admin.site.register(Photo)
admin.site.register(Comment)
admin.site.register(Rating)