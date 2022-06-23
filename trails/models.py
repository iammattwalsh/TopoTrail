from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.conf import settings

from users.models import CustomUser

from PIL import Image, ImageOps

import os

SHARE_SETTINGS = (
    ('private','Private'),
    ('public','Public'),
    ('link','Share with link'),
)

TRAIL_TYPES = {
    ('hiking','Hiking'),
    ('climbing','Climbing'),
    ('cycling','Cycling'),
}

def trail_file_location(self, filename):
    return f'{self.slug}/trail_file_{filename}'

def photo_location(self, filename):
    return f'{self.parent_trail.slug}/photos/{filename}'

def thumb_location(self, filename):
    return f'{self.parent_trail.slug}/photos/thumb-{filename}'

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
    trail_file = models.FileField(upload_to=trail_file_location,validators=[FileExtensionValidator( ['geojson','gpx','js'] ) ])
    share = models.CharField(max_length=7, choices=SHARE_SETTINGS, default='private')
    share_future = models.CharField(max_length=7, choices=SHARE_SETTINGS, default='private')
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

    def delete(self, using=None, keep_parents=False):
        files = [
            self.trail_file,
            self.heightmap,
            self.mesh,
            self.texture_sat,
            self.texture_trail,
        ]
        for file in files:
            if file != '':
                file.delete()
        super().delete()

    def __str__(self):
        return self.name

class Waypoint(models.Model):
    name = models.CharField(max_length=50)
    parent_trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
    position = models.IntegerField()
    lat = models.FloatField()
    lon = models.FloatField()
    notes = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

class Photo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent_trail = models.ForeignKey(Trail, on_delete=models.CASCADE, null=True, blank=True)
    parent_waypoint = models.ForeignKey(Waypoint, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(max_length=512, upload_to=photo_location)
    thumb = models.ImageField(max_length=512, upload_to=thumb_location, null=True, blank=True)
    caption = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.parent_trail.slug}-{self.id}'

    def create_thumb(self):
        if not self.photo:
            pass

        print(self.id)
        if not self._state.adding:
            pass

        if not os.path.isdir(f'{settings.MEDIA_ROOT}/{self.parent_trail.slug}/photos/'):
            os.mkdir(f'{settings.MEDIA_ROOT}/{self.parent_trail.slug}/photos/')

        THUMB_SIZE = (150,150)
    
        original_photo = Image.open(self.photo)

        thumb = ImageOps.fit(original_photo, THUMB_SIZE, Image.ANTIALIAS, centering=(0.5,0.5))

        thumb.save(f'{settings.MEDIA_ROOT}/{self.parent_trail.slug}/photos/thumb-{self.photo.name}')

        self.thumb.name = f'{self.parent_trail.slug}/photos/thumb-{self.photo.name}'
    
    def save(self, *args, **kwargs):
        # self.create_thumb()
        force_update = False

        if self.id:
            force_update = True
        else:
            self.create_thumb()

        super(Photo, self).save(force_update=force_update)

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
    type = models.CharField(max_length=50, choices=TRAIL_TYPES)
    trails = models.ManyToManyField(Trail)
    slug = models.SlugField(unique=True)
    # allow selection of multiple types per trail
    # does this need date added? (for future - to filter existing trails before new types are added)
    # check types above - does cycling need "off road" split between gravel and mtb?

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.type)
        super(Trail, self).save(*args, **kwargs)

    def __str__(self):
        return self.type