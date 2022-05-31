# TopoTrail

## Overview

Hikers, climbers, cyclists, and other outdoor enthusiasts are missing an important resource in understanding the areas they plan to explore: intuitively accessed tools to aid in understanding of the terrain. Terrain factors into both general supply preparation (e.g. energy expenditure requiring different trail food) and risk factoring (e.g. awareness of nearby cliffs or other terrain-based hazards).

The goal of TopoTrail is to help users understand and prepare to safely navigate trails and other outdoor terrain through 3D visualization.

TopoTrail will be built in Django and Vue, most likely using ThreeJS for 3D visualization.

## Features

---

### Story
> As a user, I want to select a trail and visualize what terrain I will encounter along it.

### Tasks 
* Create Django model for trails
* Create view that allows display and selection of trails (preferably both map and list view)
* Create view that displays trail, terrain, and additional details

---

### Story
> As a user, I want to search from available trails and select one.

### Tasks
* Implement search of trails by name or proximity to a location
* Allow filtering by criteria (type of trail - hike, bike, climb, etc - difficulty, access to water/shade)

---

### Story
> As a user, I want to upload my own trails and choose whether to make them public.

### Tasks
* Add ingestion of GeoJSON, GPX, and potentially additional formats that contain trail waypoints
* Create function that will take ingested trail data and create a 3D mesh with texture overlay displaying user's trail
* Allow sharing options including Private, Public (listed), and Public (shared link)

---

### Story
> As a user, I want to add trail details including notes about specific areas along the trail.

### Tasks
* Add trail description to Django model
* Add geo-correlated notes to model

---

### Story
> As a user, I want to step through trail waypoints and view both notes and that area's terrain highlighted.

### Tasks
* Allow camera position to move to focus on a specific location on the trail
* Modify display of trail details to highlight notes when the attached waypoint is selected

---

### Story
> As a user, I want to upload photos from my adventure on the trail.

### Tasks
* Add photo uploads linked to route model
* Assign photos to specific waypoints (automatically by geotag in EXIF??)

---

### Story
> As a user, I want to rate and comment on trails.

### Tasks
* Add rating and commenting to trails model

---

## Additional features

* API request for elevation data to construct terrain
* API request for satellite imagery to overlay on generated mesh
* Responsive design for mobile use
* Presentation view for displaying during planning

## Schema

* Trail
    - Name of trail: trail_name (charfield)
    - Latitudinal center of trail: center_lat (float)
    - Longitudinal center of trail: center_lon (float)
    - Description of trail: trail_desc (charfield)
    - List of waypoints on trail: trail_waypoint (one-to-many field)
    - Trail mesh: trail_mesh (unsure of type - charfield? Generated on submission, URL of file)
    - Trail satellite texture: trail_sat (imagefield - generated on submission, URL of file)
    - Trail route texture: trail_route (imagefield - generated on submission, URL of file)
    - Trail photos: trail_photo (one-to-many field)
    - Uploaded by: trail_uploaded (foreignkey)
    - Comments: trail_comments (foreignkey? one-to-many?)
    - Rating: trail_rating (unsure of type - collated from all user ratings)
    - Share settings (private, listed public, hidden public): trail_share (int field?)

* Waypoint
    - Latitude of point: way_lat (float)
    - Longitude of point: way_lon (float)
    - Notes on waypoint: way_note (charfield)
    - Waypoint photos: way_photo (one-to-many field)

* Comment
    - User: comment_user (foreignkey)
    - Date/time: comment_date_time (datetimefield)
    - Comment text: comment_text (charfield)

* Rating
    - User: rating_user (foreignkey)
    - Date/time: rating_date_time (datetimefield)
    - Rating: rating_score (int field)

## Schedule

### Week 1
* Create & clone repo
* Create virtual environment
* Start Django project
* Write models
* MVP of trail creation (likely without mesh/texture generation)

### Week 2
* Start CSS
* Trail name search implementation
* MVP of mesh and trail texture generation (maybe satellite, but likely saved for later)
* Add trail photos

### Week 3
* Trail geolocation search implementation
* Continue CSS
* Add sharing settings
* Add camera adjustment/movement along waypoints
* Add waypoint photos

### Week 4
* Deployment
* Add satellite texture generation
* Styling tweaks
* Add comment/rating systems
* Add presentation view

## Feature Tiers

### Must haves
* Trail creation
* Trail search by name
* Mesh and trail texture generation/display

### Should haves
* Trail search by location
* Trail photos

### Can haves
* Satellite texture generation
* Comment/rating systems
* Waypoint photos/notes
* Visual waypoint navigation
* Presentation view

### Won't haves
* 😬