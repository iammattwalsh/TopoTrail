from django.shortcuts import render
from .models import Trail, Waypoint, Photo, Comment, Rating

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
    trail = Trail.objects.get(slug=slug)
    # parse trail_file with helper function
    file_type, coords, coord_min, coord_max, coord_mid = parse_trail_file(trail)



    # two ways to do async - gather seems better

    # thingy = asyncio.get_event_loop()
    # context = thingy.create_task(async_test())
    # print(await test_var)

    # asyncio.gather(
    #     async_test()
    # )


    # thingy = asyncio.get_event_loop()
    # thingy.create_task(get_heightmap(trail,coord_mid,'SRTMGL3',30))
    asyncio.gather(
        get_heightmap(trail,coord_mid,'SRTMGL3',30)
    )

    context = {
        'file_type': file_type,
        'coords': coords,
        'coord_min': coord_min,
        'coord_max': coord_max,
        'coord_mid': coord_mid,
    }
    return render(request, 'pages/process.html', context)

####################
# HELPER FUNCTIONS #
####################

# async def async_test():
#     for i in range(1,6):
#         await asyncio.sleep(1)
#         print(str(i) + ' test test test')
#     print('end test')
#     async_test_two()
#     return 'end of test for real for real'

# def async_test_two():
#     sleep(10)
#     print('i waited for 10 whole seconds')

def parse_trail_file(trail):
    """
    Takes in trail object and parses user-uploaded file.
    """
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
    # find mid point
    coord_mid = [(coord_min[0] + coord_max[0])/2,(coord_min[1] + coord_max[1])/2]
    # update object with min/max/mid points
    trail.center_lon = coord_mid[1]
    trail.center_lat = coord_mid[0]
    trail.min_lat = coord_min[0]
    trail.min_lon = coord_min[1]
    trail.max_lat = coord_max[0]
    trail.max_lon = coord_max[1]
    trail.save()
    return file_type, coords, coord_min, coord_max, coord_mid



async def get_heightmap(trail,coord_mid,dataset,map_size):
    """
    Gets heightmap from API and saves. Returns bool based on success/failure.
    """
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
    # response = get(url, stream=True)
    if response.status_code == 200:
        response.raw.decode_content = True
        with open(f'{path}/uploads/{trail.slug}/heightmap.tif','wb') as heightmap:
            shutil.copyfileobj(response.raw, heightmap)
            trail.heightmap.name = f'{trail.slug}/heightmap.tif'
            trail.save()
            return True
    else:
        return False

def clean_heightmap():
    ...

def make_mesh(heightmap):
    ...

async def draw_trail(coords, coord_mid):
    ...

async def get_satellite():
    ...