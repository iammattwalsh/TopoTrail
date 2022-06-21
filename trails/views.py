from django.http import Http404, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Trail, Waypoint, Photo, Comment, Rating, TrailType
from .forms import NewTrailForm, AddTrailPhoto, AddTrailComment

import asyncio
import json

import geojson
import gpxpy
import gpxpy.gpx

import os
from dotenv import load_dotenv
load_dotenv()

import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None

from requests import get
import shutil
import pathlib
path = pathlib.Path(__file__).parent.parent.resolve()


##################
# VIEW FUNCTIONS #
##################

def home(request):
    context = {
        'new_trail_form': NewTrailForm(),
    }
    return render(request, 'pages/home.html', context)

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
        get_heightmap(trail,'SRTMGL3',coord_min,coord_max,coord_mid,coords),
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

@login_required
def new_trail(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        name = name.replace('#','').replace('/','')
        desc = request.POST.get('desc')
        trail_file = request.FILES.get('trail_file')
        upload_user = request.user
        timestamp = timezone.now()
        share_future = request.POST.get('share_future')
        Trail.objects.create(
            name=name,
            desc=desc,
            trail_file=trail_file,
            upload_user=upload_user,
            timestamp=timestamp,
            share_future=share_future,
        )
        this_trail = get_object_or_404(Trail, upload_user=request.user, timestamp=timestamp)
        return redirect('trails:process_upload', slug=this_trail.slug)
    context = {
        'new_trail_form': NewTrailForm()
    }
    return render(request, 'pages/new_trail.html', context)

@login_required
def edit_trail(request, slug):
    # get trail object
    trail = get_object_or_404(Trail, slug=slug)
    # authenticate user
    if trail.upload_user != request.user:
        raise Http404
    else:
        if request.method == 'POST':
            if request.POST.get('desc') != None:
                trail.desc = request.POST.get('desc')
            if request.POST.get('share') != None:
                trail.share = request.POST.get('share')
            trail.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
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
    trail_waypoints = get_list_or_404(Waypoint, parent_trail=trail)

    context = {
        'new_trail_form': NewTrailForm(),
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

def get_trail_assets(request,slug):
    trail_object = get_object_or_404(Trail, slug=slug)
    trail = {
        'name': trail_object.name,
        'desc': trail_object.desc,
        'share': trail_object.share,
        'upload_user': trail_object.upload_user.username,
        'timestamp': trail_object.timestamp,
        'slug': trail_object.slug,
        'average_rating': trail_object.average_rating,
        # 'mesh': trail_object.mesh.url,
        # 'texture_sat': trail_object.texture_sat.url,
        # 'texture_trail': trail_object.texture_trail.url,
        'status_parsed': trail_object.status_parsed,
        'status_waypoints': trail_object.status_waypoints,
        'status_heightmap': trail_object.status_heightmap,
        'status_mesh': trail_object.status_mesh,
        'status_texture_trail': trail_object.status_texture_trail,
        'status_texture_satellite': trail_object.status_texture_satellite,
        'status_overall': trail_object.status_overall,
    }
    if trail_object.mesh:
        trail['mesh'] = trail_object.mesh.url
    if trail_object.texture_sat:
        trail['texture_sat'] = trail_object.texture_sat.url
    if trail_object.texture_trail:
        trail['texture_trail'] = trail_object.texture_trail.url
    # photo_objects = get_list_or_404(Photo, parent_trail=trail_object)
    photo_objects = Photo.objects.filter(parent_trail=trail_object)
    photos = []
    for photo_object in photo_objects:
        photos.append({
            'url': photo_object.photo.url,
            'thumb':photo_object.thumb.url,
            'caption': photo_object.caption,
            'timestamp': photo_object.timestamp,
            'user': photo_object.user.username,
            'id': photo_object.id,
        })
    # comment_objects = get_list_or_404(Comment, parent_trail=trail_object)
    comment_objects = Comment.objects.filter(parent_trail=trail_object)
    comments = []
    for comment_object in comment_objects:
        comments.append({
            'user': comment_object.user.username,
            'timestamp': comment_object.timestamp,
            'comment': comment_object.comment,
        })
    return JsonResponse(data={'photos':photos,'trail':trail, 'comment':comments,})

def get_user_trails (request,slug):
    trail_object = get_object_or_404(Trail, slug=slug)
    if trail_object.upload_user == request.user:
        user_trail_objects = get_list_or_404(Trail, upload_user=trail_object.upload_user)
    else:
        user_trail_objects = get_list_or_404(Trail, upload_user=trail_object.upload_user, share='public')
    user_trails = []
    for trail in user_trail_objects:
        this_trail = {
            'name': trail.name,
            'slug': trail.slug,
            'timestamp': trail.timestamp,
            'rating': trail.average_rating,
        }
        user_trails.append(this_trail)
    return JsonResponse(data={'user_trails':user_trails})

@login_required
def add_trail_photos(request,slug):
    trail_object = get_object_or_404(Trail, slug=slug)
    if request.user == trail_object.upload_user:
        if request.FILES:
            form = AddTrailPhoto(request.POST, request.FILES)

            if form.is_valid():
                form.instance.user = request.user
                form.instance.parent_trail = trail_object
                form.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def add_trail_comment(request,slug):
    trail_object = get_object_or_404(Trail, slug=slug)
    if request.method == 'POST':
        # data = json.loads(request.body)
        # comment = data.get('comment')
        form = AddTrailComment(request.POST)

        if form.is_valid():
            form.instance.user = request.user
            form.instance.parent_trail = trail_object
            form.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def get_all_trails(request):
    trail_objects = Trail.objects.filter(share='public')
    if request.user.is_authenticated:
        user_trail_objects = Trail.objects.filter(upload_user=request.user)
    trail_list = []
    for trail in trail_objects:
        this_trail = {
            'name': trail.name,
            'slug': trail.slug,
            'upload_user': trail.upload_user.username,
            'share': trail.share,
            'timestamp': trail.timestamp,
            'average_rating': trail.average_rating,
        }
        trail_list.append(this_trail)
    if request.user.is_authenticated:
        for trail in user_trail_objects:
            if trail.share != 'public':
                this_trail = {
                    'name': trail.name,
                    'slug': trail.slug,
                    'upload_user': trail.upload_user.username,
                    'share': trail.share,
                    'timestamp': trail.timestamp,
                    'average_rating': trail.average_rating,
                }
                trail_list.append(this_trail)
    return JsonResponse(data={'trail_list':trail_list})

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
    if trail.status_mesh and trail.status_texture_trail:
        trail.share = trail.share_future
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
        if data['features'][0]['geometry']['type'] == 'LineString':
            coords = data['features'][0]['geometry']['coordinates']
        elif data['features'][0]['geometry']['type'] == 'MultiLineString':
            coords = []
            for each_list in data['features'][0]['geometry']['coordinates']:
                for each_point in each_list:
                    coords.append(each_point[:2])
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

async def get_heightmap(trail,dataset,coord_min,coord_max,coord_mid,coords):
    """
    Gets heightmap from API and saves. Returns bool based on success/failure.
    """
    # update status
    trail.status_heightmap = 0
    trail.save()
    check_status(trail)

    SECRET_KEY_OPEN_TOPOGRAPHY = os.environ.get('SECRET_KEY_OPEN_TOPOGRAPHY')
    # approximately convert miles from user input to lat/long offset value
    # size_scale = round(map_size / 120, 14)
    # # find edges of area using center point and offset value
    # north = coord_mid[0] + size_scale
    # south = coord_mid[0] - size_scale
    # east = coord_mid[1] + size_scale
    # west = coord_mid[1] - size_scale


    buffer = .05
    north = coord_max[0] + buffer
    south = coord_min[0] - buffer
    east = coord_max[1] + buffer
    west = coord_min[1] - buffer


    # grab hidden API key
    api_key = SECRET_KEY_OPEN_TOPOGRAPHY
    # build URL for request
    url = f'https://portal.opentopography.org/API/globaldem?demtype={dataset}&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff&API_Key={api_key}'
    # request from API, save image if successful and return bool
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, lambda: get(url, stream=True))
    response = await future

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

            # clean anomalies and generate mesh after success
            cleanup_generation_loop(trail,dataset,coords,coord_mid,north,south,east,west)
    else:
        # update status
        trail.status_heightmap = 0
        trail.save()
        check_status(trail)

def cleanup_generation_loop(trail,dataset,coords,coord_mid,north,south,east,west):
    """
    Handles cleanup of heightmap and generation of additional assets based on cleaned heightmap
    """
    if dataset == 'SRTMGL1':
        depth = .06 # temp value
    else:
        depth = .02 # temp value
    pixels,width,height = open_img(trail)
    pixels = find_white(pixels,width,height)
    vertices = make_verts(pixels,width,height,depth)
    polys = make_polys(width,height)
    make_obj(vertices,polys,trail,width,height)
    draw_trail(coords,coord_mid,north,south,east,west,trail,width,height)

def open_img(trail):
    """
    Opens image and handles 16-bit pixel values.
    """
    # open image and create variables
    img = Image.open(f'{path}/uploads/{trail.slug}/heightmap.tif')
    width,height = img.size
    pixels = img.load()
    # reprocess to properly use 16-bit ints
    new_pixels = []
    for y in range(height):
        new_pixels.append([])
        for x in range(width):
            new_pixels[y].append(pixels[x,y])
    img_array = np.array(new_pixels, dtype=np.uint16)
    img = Image.fromarray(img_array)
    # save reprocessed image and regenerate/return variables
    img.save(f'{path}/uploads/{trail.slug}/heightmap.tif')
    width,height = img.size
    pixels = img.load()
    return pixels,width,height

def find_white(pixels,width,height):
    """
    Scans image for anomalous white pixels and feeds them to white_correct
    when found.
    """
    # iterate through both axes
    for y in range(height):
        for x in range(width):
            # save pixel value to z variable
            z = pixels[x,y]
            # find white/error pixels and send to correction function
            if z >= 65000:
                z = white_correct(x,y,pixels,width,height)
                # change pixel value to results of cleanup
                pixels[x,y] = z
    # return cleaned pixels
    return pixels

def white_correct(x,y,pixels,width,height):
    """
    Handles anomalous white pixels formed by visible or atmospheric
    reflectivity. Finds approximate intended value by sampling adjacent
    pixels on each side and adjusting pixel value based on their distance
    from the anomalous pixel.
    """
    # lists to hold n/s/e/w values
    search = [y,y,x,x] # pixel locations
    values = [0,0,0,0] # pixel values
    distance = [0,0,0,0] # distance searched to find non-white pixel
    # set bool for each direction
    n,s,e,w = False,False,False,False
    # search for non-white pixel to the north/south
    while pixels[x,search[0]] >= 65000:
        # break if needed to avoid range error
        if search[0] == 0:
            n = True
            break
        search[0] -= 1
        distance[0] += 1
        values[0] = pixels[x,search[0]]
    while pixels[x,search[1]] >= 65000:
        # break if needed to avoid range error
        if search[1] == height - 1:
            s = True
            break
        search[1] += 1
        distance[1] += 1
        values[1] = pixels[x,search[1]]
    # copy value of other pixel on axis if a range error was avoided
    if n:
        values[0] = values[1]
    if s:
        values[1] = values[0]
    # search for non-white pixel to the east/west
    while pixels[search[2],y] >= 65000:
        # break if needed to avoid range error
        if search[2] == 0:
            e = True
            break
        search[2] -= 1
        distance[2] += 1
        values[2] = pixels[search[2],y]
    while pixels[search[3],y] >= 65000:
        # break if needed to avoid range error
        if search[3] == width - 1:
            w = True
            break
        search[3] += 1
        distance[3] += 1
        values[3] = pixels[search[3],y]
    # copy value of other pixel on axis if a range error was avoided
    if e:
        values[2] = values[3]
    if w:
        values[3] = values[2]
    # calculate total distance searched in each direction
    y_distance = abs(distance[0]) + abs(distance[1])
    x_distance = abs(distance[2]) + abs(distance[3])
    # calculate difference between values of found pixels
    tot_y_change = values[0] - values[1]
    tot_x_change = values[2] - values[3]
    # calculate what portion of that value to apply based on pixel location
    this_y_change = (tot_y_change / y_distance) * abs(distance[0])
    this_x_change = (tot_x_change / x_distance) * abs(distance[2])
    # apply pixel value change to each direction
    y_val = values[0] - this_y_change
    x_val = values[2] - this_x_change
    # combine directions and return
    return int(round((y_val + x_val) / 2,0))

def make_verts(pixels,width,height,depth):
    """
    Generates vertices from heightmap data
    """
    # create empty list to hold vertices
    vertices = []
    # iterate through all pixels
    for x in range(width):
        for y in range(height):
            # add tuple with x, y, and z coordinates to vertices list
            vertices.append((x - (width / 2),round(pixels[x,y] * depth,2),y - (height / 2)))
    # return completed list
    return vertices

def make_polys(width,height):
    """
    Generates polygons from vertices
    """
    # empty list to hold poly information
    polys = []
    # create polys referencing x/y vertices
    for x in range(width - 1):
        for y in range(height - 1):
            base = (x * height) + y
            a = base
            b = base + 1
            c = base + height + 1
            d = base + height
            # add poly pairs to list
            polys.append((a,b,c))
            polys.append((a,c,d))
    # return poly list
    return polys

def make_obj(vertices,polys,trail,width,height):
    """
    Writes .obj file with data taken from heightmap
    """
    # update status
    trail.status_mesh = 0
    trail.save()
    check_status(trail)
    # create file pased on user input
    with open(f'{path}/uploads/{trail.slug}/mesh.obj', 'w') as obj_file:
        # add vertices in format "v x-value y-value z-value"
        for vertex in vertices:
            obj_file.write(f'v {vertex[0]} {vertex[1]} {vertex[2]}\n')
        # add vertice-texture coordinates
        for x in range(width):
            for y in range(height):
                obj_file.write(f'vt {x/width} {y/height}\n')
        # add polys in format "f corner-1/vertice-texture-1 corner-2/vertice-texture-2 corner-3/vertice-texture-3"
        for poly in polys:
            obj_file.write(f'f {poly[0] + 1}/{poly[0] + 1} {poly[1] + 1}/{poly[1] + 1} {poly[2] + 1}/{poly[2] + 1}\n')
        # save to model and update status
        trail.mesh.name = f'{trail.slug}/mesh.obj'
        trail.status_mesh = 1
        trail.save()
        check_status(trail)

def draw_trail(coords,coord_mid,north,south,east,west,trail,width,height):
    """
    Draws trail texture based on coordinate inputs
    """
    trail.status_texture_trail = 0
    trail.save()
    check_status(trail)

    coord_height = north - south
    coord_width = east - west
    height_var = height/coord_height*10
    width_var = width/coord_width*10

    image_size_var = 10
    texture_trail = Image.new('RGBA', (width*image_size_var,height*image_size_var))
    draw = ImageDraw.Draw(texture_trail)

    draw.rectangle([0,0,width*image_size_var,height*image_size_var],'White')
    for i, coord in enumerate(coords):
        if i < (len(coords) - 1):
            this_coord = (((coord[1] - coord_mid[1]) * width_var) + (width * image_size_var / 2),((coord[0] - coord_mid[0]) * height_var) + (height * image_size_var / 2))
            next_coord = (((coords[i+1][1] - coord_mid[1]) * width_var) + (width * image_size_var / 2),((coords[i+1][0] - coord_mid[0]) * height_var) + (height * image_size_var / 2))
            draw.line([this_coord,next_coord],'Red',1)
    texture_trail.save(f'{path}/uploads/{trail.slug}/texture_trail.png')
    trail.texture_trail.name = f'{trail.slug}/texture_trail.png'

    trail.status_texture_trail = 1
    trail.save()
    check_status(trail)

async def get_satellite():
    ...