print("training_locations_list.py")
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, send_from_directory
##import psycopg2
import os
import time 
#from .config.config import get_config_value  
#from altmo_utils.db  import get_db_connection, get_db_pool
from altmo_utils.db import get_db_cursor
import traceback
from werkzeug.utils import secure_filename

training_locations_list_bp = Blueprint('training_locations_list', __name__)

# Initialize a list to store training locations (a tuple of name, address, latitude, longitude, and ID)
training_location = []

# Function to delete a training location from the database
def delete_training_location_from_database(id):
    with get_db_cursor(commit=True) as cursor:
   
        cursor.execute("DELETE FROM training_locations_list WHERE id = %s", (id,))
 

@training_locations_list_bp.route('/training_locations_list', methods=['GET', 'POST'])
def show_training_location():
    global training_location
    try:
        if request.method == 'POST':
            if 'function' in request.form:
                function = request.form['function']

                if function == 'delete':
                    location_ids = request.form.getlist('location_id')
                    for location_id in location_ids:
                        delete_training_location_from_database(int(location_id))

                    return redirect(url_for('training_locations_list.show_training_location'))
   
        with get_db_cursor() as cursor:
    #with get_db_connection() as conn:
     #   db_cursor = conn.cursor()
            #cursor.execute("SELECT tl.training_location, tl.training_location_address, tl.training_location_latitude, tl.training_location_longitude, tl.training_location_id, t.trainer_name,tl.training_location_picture  FROM training_locations_list tl LEFT JOIN trainer t ON tl.training_location_id = t.training_location_id ")
            cursor.execute("SELECT tl.id, tl.training_location, tl.address, tl.latitude, tl.longitude, tl.training_location_picture, t.name FROM training_locations_list tl LEFT JOIN trainer t ON tl.id = t.id")
            

            training_location = cursor.fetchall()
           # print(training_location)
            return render_template('training_locations_list.html', training_location=training_location)
    ##conn.close()
    except Exception as e:
        # Log the exception for debugging purposes
        #print(f"Error in show_training_location: {str(e)}")
        traceback.print_exc()
        return render_template('training_locations_list.html', training_location=training_location)
   # return render_template('training_locations_list.html', training_location=training_location)

#"JSON alert message code"
# Route for deleting a location and returning "JSON" response
@training_locations_list_bp.route('/delete_location', methods=['POST'])
def delete_location():
    location_ids = request.form.getlist('selected_locations')
    
    try:
        with get_db_cursor(commit=True) as cursor:
            for location_id in location_ids:
                delete_training_location_from_database(int(location_id))
            response = {
                'alert_type': 'success',
                'message': 'Selected locations deleted successfully.'
            }
    except Exception as e:
        traceback.print_exc()
        response = {
            'alert_type': 'error',
            'message': 'An error occurred while deleting the selected locations.'
        }

    return jsonify(response)

@training_locations_list_bp.route('/add_location', methods=['POST'])
def add_location():
 
    try:
        # Get the form data
        id = request.form['id']
        training_location = request.form['training_location']
        address = request.form['address']
        latitude = request.form['latitude']
        longitude = request.form['longitude']       
        # Check if a file was uploaded
        location_picture = request.files['location_picture']

        if location_picture:
            filename = secure_filename(location_picture.filename)
            relative_picture_path = os.path.join('static','training_location_pictures', filename)
            picture_path_full = os.path.join(current_app.root_path, current_app.config['TRAINING_LOCATION_PICTURES_FOLDER'], filename)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(picture_path_full), exist_ok=True)

            # Save the picture
            location_picture.save(picture_path_full)
             
            # Check if the location ID already exists
            #if any(existing_location['training_location_id'] == training_location_id for existing_location in training_location):
             #   return jsonify({'status': 'error', 'message': 'Location with this ID already exists.'})

        # Connect to the database (replace with your actual connection parameters)
        with get_db_cursor(commit=True) as cursor:
        
            cursor.execute("INSERT INTO training_locations_list (id, training_location, address, latitude,longitude, training_location_picture) VALUES (%s, %s, %s, %s, %s, %s)",
               (id, training_location, address, latitude, longitude, relative_picture_path))           
       
        return jsonify({'alert_type': 'success', 'message': 'Added a new location'})
        
    except Exception as e:
        traceback.print_exc()
        print(f"Error while saving image: {str(e)}")
        return jsonify({'alert_type': 'error', 'message': f'Error: {str(e)}'})

@training_locations_list_bp.route('/training_location_pictures/<filename>')
def display_image(filename):
    return send_from_directory(current_app.config['TRAINING_LOCATION_PICTURES_FOLDER'], filename)