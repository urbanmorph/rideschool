print("import feane/ training_locations_list.py")
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, send_from_directory
##import psycopg2
import os
import time 
#from .config.config import get_config_value  
from altmo_utils.db  import get_db_connection, get_db_pool


training_locations_list_bp = Blueprint('training_locations_list', __name__)

# Initialize a list to store training locations (a tuple of name, address, latitude, longitude, and ID)
training_location = []

# Function to delete a training location from the database
def delete_training_location_from_database(training_location_id):
    with get_db_connection() as conn:   
    #conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM training_locations_list WHERE training_location_id = %s", (training_location_id,))
    ##conn.commit()
    ##conn.close()

# Initialize a database connection
##def get_db_connection():
  ##  db_host = get_config_value('db_host')
    ##db_name = get_config_value('db_name')
    ##db_user = get_config_value('db_user')
    ##db_password = get_config_value('db_password')
    ##db_port = get_config_value('db_port')  # Add a new configuration for the database port

    ##conn = psycopg2.connect(
     ##   dbname=db_name,
       ## user=db_user,
        ##password=db_password,
        ##host=db_host,
       ## port=db_port  # Use the configured port
    ##)
    ##return conn

def get_db_connection():
    with get_db_pool().getconn() as conn:
        return conn


@training_locations_list_bp.route('/training_locations_list', methods=['GET', 'POST'])
def show_training_location():
    global training_location

    if request.method == 'POST':
        if 'function' in request.form:
            function = request.form['function']

            if function == 'delete':
                location_ids = request.form.getlist('location_id')
                for location_id in location_ids:
                    delete_training_location_from_database(int(location_id))

                return redirect(url_for('training_locations_list.show_training_location'))
   



    with get_db_connection() as conn:
        db_cursor = conn.cursor()
        db_cursor.execute("SELECT tl.training_location, tl.training_location_address, tl.training_location_latitude, tl.training_location_longitude, tl.training_location_id, t.trainer_name,tl.training_location_picture  FROM training_locations_list tl LEFT JOIN trainer t ON tl.training_location_id = t.training_location_id ")

    training_location = db_cursor.fetchall()
    ##conn.close()

    return render_template('training_locations_list.html', training_location=training_location)

#"JSON alert message code"
# Route for deleting a location and returning "JSON" response
@training_locations_list_bp.route('/delete_location', methods=['POST'])
def delete_location():
    location_ids = request.form.getlist('selected_locations')
    
    try:
        for location_id in location_ids:
            delete_training_location_from_database(int(location_id))
        response = {
            'status': 'success',
            'message': 'Selected locations deleted successfully.'
        }
    except Exception as e:
        response = {
            'status': 'error',
            'message': 'An error occurred while deleting the selected locations.'
        }

    return jsonify(response)








@training_locations_list_bp.route('/add_location', methods=['POST'])
def add_location():
    print("add_location route called")  
    try:
        # Get the form data
        training_location_id = request.form['training_location_id']
        training_location = request.form['training_location']
        training_location_address = request.form['training_location_address']
        training_location_latitude = request.form['training_location_latitude']
        training_location_longitude = request.form['training_location_longitude']

        # Check if a file was uploaded
        if 'location_picture' in request.files:
            location_picture = request.files['location_picture']
            if location_picture.filename != '':
                # Ensure the folder exists, or create it if it doesn't exist
                pictures_folder = current_app.config['TRAINING_LOCATION_PICTURES_FOLDER']

              
                os.makedirs(pictures_folder, exist_ok=True)


                # Generate a unique filename using uuid
                   # Generate a timestamp
                timestamp = int(time.time() * 1000)

                # Extract the file extension from the original filename
                _, extension = os.path.splitext(location_picture.filename)

                # Construct the unique filename
                picture_filename = f"t_location_image_{timestamp}{extension}"

                # Add the directory name "t_l_picture" to the path
                picture_path = os.path.join(pictures_folder, picture_filename)

                location_picture.save(picture_path)

                print("Picture Path:", picture_path)
                # Store the image path in the database
                image_path = picture_path
            else:
                image_path = None
        else:
            image_path = None

        # Connect to the database (replace with your actual connection parameters)
        with get_db_connection() as connection:   
    #conn = get_db_connection()
        ##cursor = conn.cursor()
        ##connection = psycopg2.connect(
          ##  host='127.0.0.1',
            ##user='postgres',
            ##password='root',
            ##dbname='Pedal_Shaale'
        ##)
            cursor = connection.cursor()

        cursor.execute("INSERT INTO training_locations_list (training_location_id, training_location, training_location_address, training_location_latitude, training_location_longitude, training_location_picture) VALUES (%s, %s, %s, %s, %s, %s)",
               (training_location_id, training_location, training_location_address, training_location_latitude, training_location_longitude, image_path))


        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        ##cursor.close()
        ##connection.close()

        # Return a success message
        return jsonify({'status': 'success', 'message': 'Location added to the database'})
        

    except Exception as e:
        print(f"Error while saving image: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'})



# The following route serves images from the TRAINING_LOCATION_PICTURES_FOLDER directory.
# It allows you to access and display images in the application.
@training_locations_list_bp.route('/static/training_location_pictures/<filename>')
def display_image(filename):
    return send_from_directory(current_app.config['TRAINING_LOCATION_PICTURES_FOLDER'], filename)