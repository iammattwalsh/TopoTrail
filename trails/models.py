from tkinter import CASCADE
from django.db import models
# from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator

from users.models import CustomUser

SHARE_SETTINGS = (
    ('private','Private'),
    ('public','Public'),
    ('link','Link'),
)

def trail_file_location(self, filename):
    return f'{self.slug}/trail_file_{filename}'

def photo_location(self, filename):
    return f'{self.slug}/photos/{filename}'

def heightmap_location(self, filename):
    return f'{self.slug}/heightmap_{filename}'

def mesh_location(self, filename):
    return f'{self.slug}/mesh_{filename}'

def texture_sat_location(self, filename):
    return f'{self.slug}/texture_sat_{filename}'

def texture_trail_location(self, filename):
    return f'{self.slug}/texture_trail_{filename}'

class Trail(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000, null=True, blank=True)
    trail_file = models.FileField(upload_to=trail_file_location,validators=[FileExtensionValidator( ['geojson','gpx'] ) ])
    share = models.CharField(max_length=7, choices=SHARE_SETTINGS, default='private')
    upload_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, null=True)
    timestamp = models.DateTimeField()
    slug = models.SlugField(unique=True, blank=True)
    average_rating = models.IntegerField(null=True, blank=True) # calculated from individual ratings
    min_lat = models.FloatField(null=True, blank=True) # generated afterward
    max_lat = models.FloatField(null=True, blank=True) # generated afterward
    min_lon = models.FloatField(null=True, blank=True) # generated afterward
    max_lon = models.FloatField(null=True, blank=True) # generated afterward
    center_lat = models.FloatField(null=True, blank=True) # generated afterward
    center_lon = models.FloatField(null=True, blank=True) # generated afterward
    heightmap = models.FileField(upload_to=heightmap_location, null=True, blank=True) # generated afterward
    mesh = models.FileField(upload_to=mesh_location, null=True, blank=True) # generated afterward
    texture_sat = models.ImageField(upload_to=texture_sat_location, null=True, blank=True) # requested afterward
    texture_trail = models.ImageField(upload_to=texture_trail_location, null=True, blank=True) # generated afterward
    
    status_parsed = models.FloatField(default=0) # auto-calculated during generation
    status_waypoints = models.FloatField(default=0) # auto-calculated during generation
    status_heightmap = models.FloatField(default=0) # auto-calculated during generation
    status_mesh = models.FloatField(default=0) # auto-calculated during generation
    status_texture_trail = models.FloatField(default=0) # auto-calculated during generation
    status_texture_satellite = models.FloatField(default=0) # auto-calculated during generation
    status_overall = models.FloatField(default=0) # auto-calculated during generation

    # ForeignKeys: (*=written)
    # *waypoints
    # photos
    # comments
    # rating

    def save(self, *args, **kwargs):
        if not self.slug:
            # find number of matching names that would cause a duplicate slug
            matching_slugs = Trail.objects.filter(name=self.name).count()
            # add a number to the end of the slug if matches exist
            if matching_slugs > 0:
                self.slug = slugify(self.name + '-' + str(matching_slugs))
            # make a regular slug if no matches exist
            else:
                self.slug = slugify(self.name)
        super(Trail, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Waypoint(models.Model):
    name = models.CharField(max_length=50)
    parent_trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
    position = models.IntegerField()
    lat = models.FloatField()
    lon = models.FloatField()
    notes = models.CharField(max_length=200, null=True, blank=True)

    # ForeignKeys: (*=written)
    # photos

    def __str__(self):
        return self.name

class Photo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent_trail = models.ForeignKey(Trail, on_delete=models.CASCADE, null=True, blank=True)
    parent_waypoint = models.ForeignKey(Waypoint, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to=photo_location)
    caption = models.CharField(max_length=100)

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent_trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=500)

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent_trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

class TrailType(models.Model):
    # type of trail - (climbing, hiking, cycling, etc)
    # allow selection of multiple
    ...