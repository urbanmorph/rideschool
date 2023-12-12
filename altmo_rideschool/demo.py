import folium

# Step 1: Create a Folium map centered at a specific location (latitude, longitude)
map_center = [37.7749, -122.4194]  # Replace with the desired center coordinates
my_map = folium.Map(location=map_center, zoom_start=13)  # You can adjust the zoom level

# Step 2: Add a marker to the map at a specific location (latitude, longitude)
marker_location = [37.7749, -122.4194]  # Replace with the desired marker coordinates
folium.Marker(location=marker_location, popup='Marker Popup Text').add_to(my_map)

# Step 3: Save the map to an HTML file
my_map.save('my_map.html')



import folium

# Step 1: Create a Folium map centered at Bangalore's location
bangalore_center = [12.9716, 77.5946]  # Bangalore's coordinates
my_map = folium.Map(location=bangalore_center, zoom_start=13)  # You can adjust the zoom level

# Step 2: Add a marker to the map at a specific location within Bangalore
marker_location = [12.9716, 77.5946]  # You can adjust these coordinates
folium.Marker(location=marker_location, popup='Marker Popup Text').add_to(my_map)

# Step 3: Save the map to an HTML file
my_map.save('my_map.html')

###

import folium
from db import get_db_cursor

def fetch_locations_from_db():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT training_location_latitude, training_location_longitude FROM training_locations_list")
        locations = cursor.fetchall()
    return locations

def create_folium_map(locations):
    # Step 1: Create a Folium map centered at the first location in the result set
    if locations:
        map_center = [locations[0]['training_location_latitude'], locations[0]['training_location_longitude']]
    else:
        # If there are no locations in the result set, fallback to a default center
        map_center = [12.9716, 77.5946]

    my_map = folium.Map(location=map_center, zoom_start=13)  # You can adjust the zoom level

    # Step 2: Add markers to the map for each location in the result set
    for location in locations:
        marker_location = [location['training_location_latitude'], location['training_location_longitude']]
        folium.Marker(location=marker_location, popup='Marker Popup Text').add_to(my_map)

    # Step 3: Save the map to an HTML file
    my_map.save('my_map.html')

if __name__ == "__main__":
    # Fetch locations from the database
    locations = fetch_locations_from_db()

    # Create a Folium map with the fetched locations
    create_folium_map(locations)



##########
# map_bp.py

from flask import Blueprint, render_template
from folium import Map, Marker
from .db import get_db_cursor

map_bp = Blueprint('map', __name__)

@map_bp.route('/create_map')
def create_map():
    locations = fetch_locations_from_db()
    create_folium_map(locations)
    return render_template('map_created.html')  # You can create a simple HTML template to indicate that the map is created

def fetch_locations_from_db():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT training_location_latitude, training_location_longitude FROM training_locations_list")
        locations = cursor.fetchall()
    return locations

def create_folium_map(locations):
    # Step 1: Create a Folium map centered at the first location in the result set
    if locations:
        map_center = [locations[0]['training_location_latitude'], locations[0]['training_location_longitude']]
    else:
        # If there are no locations in the result set, fallback to a default center
        map_center = [12.9716, 77.5946]

    my_map = Map(location=map_center, zoom_start=13)  # You can adjust the zoom level

    # Step 2: Add markers to the map for each location in the result set
    for location in locations:
        marker_location = [location['training_location_latitude'], location['training_location_longitude']]
        Marker(location=marker_location, popup='Marker Popup Text').add_to(my_map)

    # Step 3: Save the map to an HTML file
    my_map.save('my_map.html')


init.py
# init.py

import os
from flask import Flask, render_template
from flask_session import Session
from .admin import admin_bp
from .logins import logins_bp
from .participant import participant_bp
from .sessions import sessions_bp
from .signup import signup_bp
from .summary import summary_bp
from .trainer import trainer_bp
from .training_locations_list import training_locations_list_bp
from .organization import organization_bp
from .map_bp import map_bp  # Import the map blueprint
from altmo_utils import db 
import atexit 
import json 

_version_ = '1.0.0'

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_file("config.json", load=json.load)
    else:
        app.config.from_mapping(test_config)

    app.secret_key = app.config.get('SECRET_KEY', 'default_secret_key')
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['CSRF_ENABLED'] = True

    app.config['UPLOAD_FOLDER'] = app.config.get('UPLOAD_FOLDER', 'static/uploaded_images')
    app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = app.config.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/training_location_pictures')
    app.config['ORGANIZATION_FOLDER'] = app.config.get('ORGANIZATION_FOLDER', 'static/organization_image')

    app.static_folder = 'static'
    app.config["DB_URL"] = app.config.get("DATABASE_URI")

    db.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/FAQ.html')
    def about():
        return render_template('FAQ.html')

    app.register_blueprint(participant_bp)
    app.register_blueprint(trainer_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(logins_bp)
    app.register_blueprint(training_locations_list_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(organization_bp)
    app.register_blueprint(map_bp)  # Register the map blueprint

    atexit.register(db.close_db_pool)
    return app

rideschool_app = create_app()


