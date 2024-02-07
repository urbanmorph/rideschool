from flask import Blueprint, render_template
import folium
from altmo_utils.db import get_db_cursor 

#from map_blueprint import map_bp
map_bp = Blueprint('map', __name__)

def fetch_locations_from_db():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT latitude, longitude FROM training_locations_list")
        locations = cursor.fetchall()
    return locations

def create_folium_map(locations):
    # Step 1: Create a Folium map centered at the first location in the result set
    ##if locations:
      ##  map_center = [locations[0]['training_location_latitude'], locations[0]['training_location_longitude']]
    ##else:
        # If there are no locations in the result set, fallback to a default center
        ##map_center = [12.9716, 77.5946] # note if u r uncommenting this line then you need to uncomment the below  line (b_line)
    map_center = [12.9716, 77.5946] # b_line 

    my_map = folium.Map(location=map_center, zoom_start=13)  # You can adjust the zoom level

    # Step 2: Add markers to the map for each location in the result set
    for location in locations:
        marker_location = [location['latitude'], location['longitude']]
        folium.Marker(location=marker_location, popup='Marker Popup Text').add_to(my_map)

    # Step 3: Save the map to an HTML file
    my_map.save('map.html')



@map_bp.route('/map')
def show_map():
    #In this /map route, the locations are fetched from the database using fetch_locations_from_db()
    # Fetch locations from the database
    locations = fetch_locations_from_db()

    #The create_folium_map function is then called with these fetched locations to create a dynamic map based on the current state of the database.

    # Create a Folium map with the fetched locations
    create_folium_map(locations)
    
    # You may redirect to the HTML page where you display the map
   # return render_template('map.html')
    print(locations)
    return render_template('map.html', locations=locations)

