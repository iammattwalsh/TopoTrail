from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

SHARE_SETTINGS = (
    ('private','Private'),
    ('public','Public'),
    ('link','Link'),
)

def trail_file_location(self, filename):
    return f'{self.slug}/trail_file_{filename}'

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
    desc = models.CharField(max_length=500)
    trail_file = models.FileField(upload_to=trail_file_location,validators=[FileExtensionValidator( ['geojson','gpx'] ) ])
    share = models.CharField(max_length=7, choices=SHARE_SETTINGS, default='private')
    upload_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    slug = models.SlugField(unique=True, blank=True)
    min_lat = models.FloatField(null=True, blank=True) # generated afterward
    max_lat = models.FloatField(null=True, blank=True) # generated afterward
    min_lon = models.FloatField(null=True, blank=True) # generated afterward
    max_lon = models.FloatField(null=True, blank=True) # generated afterward
    center_lat = models.FloatField(null=True, blank=True) # generated afterward
    center_lon = models.FloatField(null=True, blank=True) # generated afterward
    heightmap = models.FileField(upload_to=heightmap_location,null=True, blank=True) # generated afterward
    mesh = models.FileField(upload_to=mesh_location,null=True, blank=True) # generated afterward
    texture_sat = models.ImageField(upload_to=texture_sat_location,null=True, blank=True) # requested afterward
    texture_trail = models.ImageField(upload_to=texture_trail_location,null=True, blank=True) # generated afterward

    # ForeignKeys: (*=written)
    # *waypoints
    # photos
    # comments
    # rating

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Trail, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Waypoint(models.Model):
    parent_trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
    position = models.IntegerField()
    lat = models.FloatField()
    lon = models.FloatField()
    notes = models.CharField(max_length=200)

    # ForeignKeys: (*=written)
    # photos

class Photo(models.Model):
    ...

class Comment(models.Model):
    ...

class Rating(models.Model):
    ...