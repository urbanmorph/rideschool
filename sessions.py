from flask import Blueprint, render_template, request, send_from_directory, jsonify, current_app, session
import os
import psycopg2
import logging
from datetime import datetime
from config.config import get_config_value 



sessions_bp = Blueprint('sessions', __name__)

# Create a database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=get_config_value('db_host'),
        port=get_config_value('db_port'),  # If port is a configuration value
        database=get_config_value('db_name'),
        user=get_config_value('db_user'),
        password=get_config_value('db_password')
    )
    conn.set_session(autocommit=True)
    return conn



# Initialize the database if it does not exist
def create_database():
    conn = psycopg2.connect(
        host=get_config_value('db_host'),
        port=get_config_value('db_port'),  # If port is a configuration value
        database=get_config_value('db_name'),
        user=get_config_value('db_user'),
        password=get_config_value('db_password')
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database WHERE datname='Pedal_Shaale'")
    if not cursor.fetchone():
        cursor.execute('CREATE DATABASE Pedal_Shaale')
    cursor.close()
    conn.close()

@sessions_bp.route('/')
def index():
    return "Hello, this is the root URL!"

@sessions_bp.route('/session_form')
def form():
    try:
        # Fetch the certified trainer names from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT trainer_id, trainer_name FROM trainer WHERE trainer_status = %s", ('CERTIFIED',))
        trainers = [{'trainer_id': row[0], 'trainer_name': row[1]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        

          # Get the currently logged-in trainer's name from the session (replace with your actual session data)
        current_trainer_name = session.get('trainer_name', '')  # Use session['trainer_name'] if that's how you access it

        return render_template('sessions_form.html', trainers=trainers, current_trainer_name=current_trainer_name)
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching certified trainer names. Please try again later.'

@sessions_bp.route('/trainers')
def get_trainers():
    try:
        # Fetch the trainer names and statuses from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT trainer_id, trainer_name, trainer_status FROM trainer")
        trainers = [{'trainer_id': row[0], 'trainer_name': row[1], 'trainer_status': row[2]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify(trainers)
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return jsonify([])

@sessions_bp.route('/trainer/<int:trainer_id>')
def get_trainer(trainer_id):
    try:
        # Fetch the training_location_id for the selected trainer
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT training_location_id FROM trainer WHERE trainer_id = %s", (trainer_id,))
        training_location_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return jsonify({'training_location_id': training_location_id})
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return jsonify({})

@sessions_bp.route('/participants/<int:trainer_id>')
def get_participants(trainer_id):
    try:
        print("Fetching participants for Trainer ID:", trainer_id)  # Add this line for debugging

        # Fetch the training_location_id for the selected trainer
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT training_location_id FROM trainer WHERE trainer_id = %s", (trainer_id,))
        result = cursor.fetchone()

        if result is None:
            return jsonify([])  # Return an empty list if no training_location_id found

        training_location_id = result[0]

        # Fetch the participants based on the matching training_location_id, participant_status as "NEW" or "ONGOING",
        # and exclude those with participant_status as "COMPLETED"
        cursor.execute(
            "SELECT participant_name FROM participants WHERE training_location_id = %s AND participant_status IN ('NEW', 'ONGOING') AND participant_name NOT IN (SELECT participant_name FROM participants WHERE participant_status = 'COMPLETED')",
            (training_location_id,))
        participants = [{'participant_name': row[0]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify(participants)
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return jsonify([])

@sessions_bp.route('/participant/<string:participant_name>')
def get_participant(participant_name):
    try:
        # Fetch the participant details based on the given participant_name
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM participants WHERE participant_name = %s", (participant_name,))
        participant = cursor.fetchone()
        cursor.close()
        conn.close()

        if participant is None:
            return jsonify({}), 404  # Return an empty response with 404 status if participant is not found
        print("Participant:", participant)  # Added print statement

        # You can return more fields from the participants table if needed
        return jsonify({
            'participant_name': participant[0],
            'training_location_id': participant[1],
            # Add other fields from the participants table as needed
        })

    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return jsonify({}), 500  # Return an empty response with 500 status for any error

@sessions_bp.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        print("Form data:", request.form)  # Add this line for debugging
        
        # Rest of the code to process the form data
        trainer_id = request.form['trainer-id']  # Retrieve the trainer_id from the hidden input
        participant_name = request.form['participant-name']
        scheduled_datetime = request.form['scheduled-datetime']
        actual_datetime = request.form['actual-datetime']
        hours_trained = request.form['hours-trained']
        picture = request.files['session-picture']
        video = request.files['session-video']
        description = request.form['session-description']

           # Fetch the trainer_id and participant_id based on the names
        conn = get_db_connection()
        cursor = conn.cursor()

 # Fetch participant_id based on participant_name
    
        cursor.execute("SELECT participant_id FROM participants WHERE participant_name = %s", (participant_name,))
        participant_id = cursor.fetchone()

        if participant_id is not None:
            participant_id = participant_id[0]
        else:
            # Handle the case where the participant is not found
            return jsonify({'status': 'error', 'message': 'Participant not found'})

       # Check if this is the first session entry for the participant
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE participant_id = %s", (participant_id,))
        session_count = cursor.fetchone()[0]

        # If this is the first session, update participant status to 'ONGOING'
        if session_count == 0:
            cursor.execute("UPDATE participants SET participant_status = 'ONGOING' WHERE participant_id = %s", (participant_id,))
            conn.commit()



       
        # Save the image and video files to the uploaded_image folder under the static folder
        picture_filename = picture.filename
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)
        picture.save(os.path.join(current_app.root_path, picture_path))

        video_filename = video.filename
        video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video_filename)
        video.save(os.path.join(current_app.root_path, video_path))

        # Insert the data into the database
        
        cursor.execute('''
            INSERT INTO sessions (
                trainer_id,  -- Store the trainer_id
                participant_id, 
                scheduled_datetime, 
                actual_datetime, 
                hours_trained, 
                picture_path, 
                video_path, 
                description
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (trainer_id, participant_id, scheduled_datetime, actual_datetime, hours_trained,
              picture_path, video_path, description))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Form submitted successfully!'})
    except Exception as e:
        # Handle errors and rollback the transaction if needed
        if conn:
            conn.rollback()
            conn.close()
        logging.error("An error occurred:", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Error submitting the form. Please try again later.'})

#When a trainer logs in and is authenticated, their trainer_id is stored in the session along with other relevant information, such as their name (trainer_name),,When the form is submitted to the /submit_form route, the value of the hidden input field named "trainer-id" is extracted from the form data using request.form['trainer-id']. This value corresponds to the trainer_id of the currently logged-in trainer.. In this way, the trainer_id is carried through the hidden input field from the session to the form submission. This approach helps ensure that the data is associated with the correct trainer and maintains data integrity throughout the form submission process


@sessions_bp.route('/sessions_table')
def sessions_table():
    try:
        # Fetch session data from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions')
        sessions = cursor.fetchall()
        cursor.close()
        conn.close()
        

        return render_template('sessions_table.html', sessions=sessions)

    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching session data. Please try again later.'

@sessions_bp.route('/uploaded_image/<filename>')
def display_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)




