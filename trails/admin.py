from django.contrib import admin
from .models import Trail, Waypoint, Photo, Comment, Rating, TrailType

admin.site.register(Trail)
admin.site.register(Waypoint)
admin.site.register(Photo)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(TrailType)