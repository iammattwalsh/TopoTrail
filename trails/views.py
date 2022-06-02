from django.shortcuts import render
from .models import Trail, Waypoint, Photo, Comment, Rating

import geojson
import gpxpy
import gpxpy.gpx

def home(request):
    return render(request, 'pages/home.html')

def process_upload(request, slug):
    trail = Trail.objects.get(slug=slug)
    trail_file = trail.trail_file.path
    if str(trail_file).endswith('.geojson'):
        with open(trail_file) as f:
            data = geojson.load(f)
        coords = data['features'][0]['geometry']['coordinates'] # may be able to clean up - look into geojson module more
        file_check = 'geojson'
        print('geojson')
    elif str(trail_file).endswith('.gpx'):
        with open(trail_file) as f:
            data = gpxpy.parse(f)
        coords = []
        for track in data.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coords.append([point.latitude, point.longitude])
        file_check = 'gpx'
        print('gpx')

    print(trail_file)
    context = {
        'file_check': file_check,
        'coords': coords,
    }
    return render(request, 'pages/process.html', context)




# test to make sure initiated code will continue to run after page close
# import time
# def test(request):
#     time.sleep(2)
#     print('ping1')
#     time.sleep(2)
#     print('ping2')
#     time.sleep(2)
#     print('ping3')
#     time.sleep(2)
#     print('ping4')
#     time.sleep(2)
#     print('ping5')
#     time.sleep(2)
#     print('ping6')
#     time.sleep(2)
#     print('ping7')
#     time.sleep(2)
#     print('ping8')
#     time.sleep(2)
#     print('ping9')
#     time.sleep(2)
#     print('ping10')
#     return render(request, 'pages/home.html')