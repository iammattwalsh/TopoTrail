from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone

from .models import Trail, Waypoint, Photo, Comment, Rating, TrailType
from .forms import NewTrailForm

import asyncio
from time import sleep

import geojson
import gpxpy
import gpxpy.gpx

import os
from dotenv import load_dotenv
load_dotenv()

from requests import get
import shutil
import pathlib
path = pathlib.Path(__file__).parent.parent.resolve()


##################
# VIEW FUNCTIONS #
##################

def home(request):
    return render(request, 'pages/home.html')

async def process_upload(request, slug):
    # get trail object
    trail = get_object_or_404(Trail, slug=slug)
    # trail = Trail.objects.get(slug=slug)
    # parse trail_file with helper function
    file_type, coords, coord_min, coord_max, coord_mid = parse_trail_file(trail)



    # BELOW LINES ONLY EXIST FOR REFERENCE
    # two ways to do async - gather seems better

    # thingy = asyncio.get_event_loop()
    # context = thingy.create_task(async_test())
    # print(await test_var)

    # asyncio.gather(
    #     async_test()
    # )
    # ABOVE LINES ONLY EXIST FOR REFERENCE


    asyncio.gather(
        get_heightmap(trail,coord_mid,'SRTMGL3',30),
        make_waypoints(coords, trail),
    )

    # context = {
    #     'file_type': file_type,
    #     'coords': coords,
    #     'coord_min': coord_min,
    #     'coord_max': coord_max,
    #     'coord_mid': coord_mid,
    # }
    return redirect('trails:view_trail', slug=trail.slug)
    # return render(request, 'pages/process.html', context)

def new_trail(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        trail_file = request.FILES.get('trail_file')
        upload_user = request.user
        timestamp = timezone.now()
        Trail.objects.create(
            name=name,
            desc=desc,
            trail_file=trail_file,
            upload_user=upload_user,
            timestamp=timestamp
        )
        this_trail = get_object_or_404(Trail, upload_user=request.user, timestamp=timestamp)
        return redirect('trails:process_upload', slug=this_trail.slug)
    context = {
        'new_trail_form': NewTrailForm()
    }
    return render(request, 'pages/new_trail.html', context)

def edit_trail(request, slug):
    # get trail object
    trail = get_object_or_404(Trail, slug=slug)
    # authenticate user
    if trail.upload_user != request.user:
        raise Http404
    else:
        if request.method == 'POST':
            trail.desc = request.POST.get('desc')
            trail.save()
            return redirect('trails:view_trail', slug=trail.slug)

def delete_trail(request, slug):
    # get trail object
    trail = get_object_or_404(Trail, slug=slug)
    # authenticate user
    if trail.upload_user != request.user:
        raise Http404
    else:
        if request.method == 'POST':
            trail.delete()
            return redirect('trails:home')

def view_trail(request, slug):
    # get trail object
    trail = get_object_or_404(Trail, slug=slug)
    # get waypoint objects
    trail_waypoints = Waypoint.objects.filter(parent_trail=trail)

    context = {
        'trail': trail,
        'trail_waypoints': trail_waypoints,        
    }
    return render(request, 'pages/trail.html', context)

def rate_trail(request, slug):
    """
    Saves individual rating and updates trail's overall rating
    """
    # update_trail_rating(trail)
    ...

####################
# HELPER FUNCTIONS #
####################

def check_status(trail):
    """
    Calculates overall generation status based on task status
    """
    if trail.status_parsed and trail.status_waypoints and trail.status_heightmap and trail.status_mesh and trail.status_texture_trail and trail.status_texture_satellite:
        trail.status_overall = 1
        trail.save()
    else:
        trail.status_overall = (trail.status_parsed + trail.status_waypoints + trail.status_heightmap + trail.status_mesh + trail.status_texture_trail + trail.status_texture_satellite) / 6
        trail.save()

def update_trail_rating(trail):
    """
    Updates trail's rating from individual ratings
    """
    ...

async def make_waypoints(coords, trail):
    """
    Takes in list of coordinates and makes objects from them.
    """
    # iterate over coordinates with value and index
    try:
        for i, coord in enumerate(coords):
            # look for an object to update or create a new one
            this_waypoint, created = Waypoint.objects.get_or_create(
                name = f'{trail.slug}:{i}',
                defaults = {
                    'name': f'{trail.slug}:{i}',
                    'parent_trail': trail,
                    'position': i,
                    'lat': coord[0],
                    'lon': coord[1],
                }
            )

            # update status
            # trail.status_waypoints = round((i + 1) / len(coords), 2)
            # trail.save()
            # check_status(trail)
        # update status
        trail.status_waypoints = 1
        trail.save()
        check_status(trail)
    except:
        # update status
        trail.status_waypoints = 0
        trail.save()
        check_status(trail)

def parse_trail_file(trail):
    """
    Takes in trail object and parses user-uploaded file.
    """
    # update status
    trail.status_parsed = 0
    trail.save()
    check_status(trail)

    trail_file = trail.trail_file.path
    # parse geojson
    if str(trail_file).endswith('.geojson'):
        with open(trail_file) as f:
            data = geojson.load(f)
        coords = data['features'][0]['geometry']['coordinates']
        # convert lon,lat formatting to lat,lon
        for point in coords:
            point.reverse()
        file_type = 'geojson'
    # parse gpx
    elif str(trail_file).endswith('.gpx'):
        with open(trail_file) as f:
            data = gpxpy.parse(f)
        coords = []
        for track in data.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coords.append([point.latitude, point.longitude])
        file_type = 'gpx'
    
    # update status
    # trail.status_parsed = .25
    # trail.save()
    # check_status(trail)

    # set min/max points to first point
    coord_min = [coords[0][0],coords[0][1]]
    coord_max = [coords[0][0],coords[0][1]]
    # iterate over coordinates to find min/max lat/lon points
    for point in coords:
        # find min/max lat
        if point[0] < coord_min[0]:
            coord_min[0] = point[0]
        elif point[0] > coord_max[0]:
            coord_max[0] = point[0]
        # find min/max lon
        if point[1] < coord_min[1]:
            coord_min[1] = point[1]
        elif point[1] > coord_max[1]:
            coord_max[1] = point[1]
    
    # update status
    # trail.status_parsed = .5
    # trail.save()
    # check_status(trail)

    # find mid point
    coord_mid = [(coord_min[0] + coord_max[0])/2,(coord_min[1] + coord_max[1])/2]

    # update status
    # trail.status_parsed = .75
    # trail.save()
    # check_status(trail)

    # update object with min/max/mid points
    trail.center_lon = coord_mid[1]
    trail.center_lat = coord_mid[0]
    trail.min_lat = coord_min[0]
    trail.min_lon = coord_min[1]
    trail.max_lat = coord_max[0]
    trail.max_lon = coord_max[1]
    # update status
    trail.status_parsed = 1
    trail.save()
    check_status(trail)
    return file_type, coords, coord_min, coord_max, coord_mid

async def get_heightmap(trail,coord_mid,dataset,map_size):
    """
    Gets heightmap from API and saves. Returns bool based on success/failure.
    """
    # update status
    trail.status_heightmap = 0
    trail.save()
    check_status(trail)

    SECRET_KEY_OPEN_TOPOGRAPHY = os.environ.get('SECRET_KEY_OPEN_TOPOGRAPHY')
    # approximately convert miles from user input to lat/long offset value
    size_scale = round(map_size / 120, 14)
    # find edges of area using center point and offset value
    north = coord_mid[0] + size_scale
    south = coord_mid[0] - size_scale
    east = coord_mid[1] + size_scale
    west = coord_mid[1] - size_scale
    # grab hidden API key
    api_key = SECRET_KEY_OPEN_TOPOGRAPHY
    # build URL for request
    url = f'https://portal.opentopography.org/API/globaldem?demtype={dataset}&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff&API_Key={api_key}'
    # request from API, save image if successful and return bool
    loop = asyncio.get_event_loop()
    future1 = loop.run_in_executor(None, lambda: get(url, stream=True))
    response = await future1

    # update status
    # trail.status_heightmap = .25
    # trail.save()
    # check_status(trail)

    # response = get(url, stream=True)
    if response.status_code == 200:
        response.raw.decode_content = True
        with open(f'{path}/uploads/{trail.slug}/heightmap.tif','wb') as heightmap:

            # update status
            # trail.status_heightmap = .5
            # trail.save()
            # check_status(trail)

            shutil.copyfileobj(response.raw, heightmap)

            # update status
            # trail.status_heightmap = .75
            # trail.save()
            # check_status(trail)

            trail.heightmap.name = f'{trail.slug}/heightmap.tif'

            # update status
            trail.status_heightmap = 1
            trail.save()
            check_status(trail)
    else:
        # update status
        trail.status_heightmap = 0
        trail.save()
        check_status(trail)

def clean_heightmap():
    ...

async def make_mesh(heightmap):
    ...

async def draw_trail(coords, coord_mid):
    ...

async def get_satellite():
    ...