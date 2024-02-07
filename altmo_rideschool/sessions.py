print("import feane/ sessions.py")
from flask import Blueprint, render_template, request, send_from_directory, jsonify, current_app, session
import os
import logging
from datetime import datetime
from altmo_utils.db import get_db_cursor
import traceback

sessions_bp = Blueprint('sessions', __name__)

# Initialize the database if it does not exist
def create_database():   
    with get_db_cursor() as cursor:
        cursor.execute("SELECT datname FROM pg_database WHERE datname='Pedal_Shaale'")
        if not cursor.fetchone():
            cursor.execute('CREATE DATABASE Pedal_Shaale')
   
@sessions_bp.route('/session_form')
def form():
    try:
        # Fetch the certified trainer names from the database       
        with get_db_cursor() as cursor:            
            cursor.execute("SELECT id, name FROM trainer WHERE status = %s", ('CERTIFIED',))
            rows = cursor.fetchall()            
            
            trainers = [{'id': row['id'], 'name': row['name']} for row in rows]               
            current_trainer_name = session.get('name', '')  
            return render_template('sessions_form.html', trainers=trainers, current_trainer_name=current_trainer_name)
    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        return jsonify({'alert_type ': 'error', 'message': 'Error fetching certified trainer names. Please try again later.'})

@sessions_bp.route('/trainers')
def get_trainers():
    try:
        # Fetch the trainer names and statuses from the database
        with get_db_cursor() as cursor:        
            cursor.execute("SELECT id, name, status FROM trainer")          
            trainers = [{'id': row['id'], 'name': row['name'], 'status': row['status']} for row in cursor.fetchall()]       

        return jsonify(trainers)
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return jsonify([])

@sessions_bp.route('/trainer/<int:trainer_id>')
def get_trainer(trainer_id):
    try:
        # Fetch the training_location_id for the selected trainer
        with get_db_cursor() as cursor:        
            cursor.execute("SELECT t_location_id FROM trainer WHERE id = %s", (trainer_id,))
            training_location_id = cursor.fetchone().get('t_location_id', None)
        return jsonify({'t_location_id': training_location_id})
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return jsonify({})

@sessions_bp.route('/participants/<int:trainer_id>')
def get_participants(trainer_id):
    try:
        # Fetch the training_location_id for the selected trainer        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT t_location_id FROM trainer WHERE id = %s", (trainer_id,))
            result = cursor.fetchone()
            if result is None:
                return jsonify([])  # Return an empty list if no training_location_id is found

            training_location_id = result.get('t_location_id', None)

        # Fetch the participants based on the matching training_location_id, participant_status as "NEW" or "ONGOING",and exclude those with participant_status as "COMPLETED"
            cursor.execute(
                "SELECT name FROM participants WHERE t_location_id = %s AND status IN ('NEW', 'ONGOING') AND name NOT IN (SELECT name FROM participants WHERE status = 'COMPLETED')",
                (training_location_id,))
     
            participants = [{'name': row.get('name')} for row in cursor.fetchall()]    
            #print("Fetched Participants:", participants)
            return jsonify(participants)
    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        return jsonify([])

@sessions_bp.route('/participant/<int:participant_id>')
def get_participant(participant_id):
    try:
        # Fetch the participant details based on the given participant_name
        with get_db_cursor() as cursor:  
            cursor.execute("SELECT * FROM participants WHERE id = %s", (participant_id,))          
            #cursor.execute("SELECT * FROM participants WHERE participant_name = %s", (participant_name,))
            participant = cursor.fetchone()        
            if participant is None:
                return jsonify({}), 404  # Return an empty response with 404 status if participant is not found
       
            return jsonify({            
                'name': participant['name'],  
                't_location_id': participant['t_location_id'],            
            })
    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        return jsonify({}), 500  # Return an empty response with 500 status for any error

@sessions_bp.route('/submit_form', methods=['POST'])
def submit_form():
    try:             
        # trainer_id = request.form.get('trainer-id') # only if i use " data: formdata ;" and this var formData = $(this).serialize(); to send the data to the server  
        trainer_id = request.form['trainer-id']  # Retrieve the trainer_id from the hidden input and i am using this in $.alax --data: new FormData(this),
        participant_name = request.form['participant-name']
        scheduled_datetime = request.form['scheduled-datetime']
        actual_datetime = request.form['actual-datetime']
        hours_trained = request.form['hours-trained']
        picture = request.files['session-picture']
        video = request.files['session-video']
        description = request.form['session-description']

        # Fetch the trainer_id and participant_id based on the names
        with get_db_cursor(commit=True) as cursor:        
            # Fetch participant_id based on participant_name    
            cursor.execute("SELECT id FROM participants WHERE name = %s", (participant_name,))
            participant_id = cursor.fetchone()

            if participant_id is not None:
                #participant_id = participant_id[0]
                participant_id = participant_id['id']
            else:
                # Handle the case where the participant is not found
                return jsonify({'alert_type ': 'error', 'message': 'Participant not found'})

            # Check if this is the first session entry for the participant
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE participant_id = %s", (participant_id,))
            #session_count = cursor.fetchone()[0]
            session_count = cursor.fetchone()['count']
            #determine the session status
            session_status = 'ONGOING' if session_count > 0 else 'NEW'

            # If this is the first session, update participant status to 'ONGOING'
            if session_count == 0:
                cursor.execute("UPDATE participants SET status = 'ONGOING', training_start = %s WHERE id = %s", (actual_datetime, participant_id,))
                
            # Save the image and video files to the uploaded_images folder under the static folder
            picture_filename = picture.filename
            picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)
            # picture.save(os.path.join(current_app.root_path, picture_path))
            picture_path_full = os.path.join(current_app.root_path, picture_path)

            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(picture_path_full), exist_ok=True)
            # Save the image and video files to the uploaded_images folder under the static folder
            picture.save(picture_path_full)

            video_filename = video.filename
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video_filename)
            video.save(os.path.join(current_app.root_path, video_path))

            # Insert the data into the database        
            cursor.execute('''
                INSERT INTO sessions (
                    trainer_id,  -- Store the trainer_id
                    participant_id, 
                    scheduled_datetime, 
                    actual_date, 
                    hours_trained, 
                    picture_path, 
                    video_path, 
                    description,
                    status
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
            ''', (trainer_id, participant_id, scheduled_datetime, actual_datetime, hours_trained,
                  picture_path, video_path, description, session_status))
            
        return jsonify({'alert_type ': 'success', 'message': 'Submitted successfully!'})
    except Exception as e:
            traceback.print_exc()
        # Handle errors and rollback the transaction if needed        
            logging.error("An error occurred:", exc_info=True)
            return jsonify({'alert_type ': 'error', 'message': 'Error submitting the form. Please try again later.'})

#When a trainer logs in and is authenticated, their trainer_id is stored in the session along with other relevant information, such as their name (trainer name),,When the form is submitted to the /submit_form route, the value of the hidden input field named "trainer-id" is extracted from the form data using request.form['trainer-id']. This value corresponds to the trainer_id of the currently logged-in trainer.. In this way, the trainer_id is carried through the hidden input field from the session to the form submission. This approach helps ensure that the data is associated with the correct trainer and maintains data integrity throughout the form submission process
@sessions_bp.route('/sessions_table')
def sessions_table():
    try:
        # Fetch session data from the database
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM sessions')
            sessions = cursor.fetchall()
            return render_template('sessions_table.html', sessions=sessions)
    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        #return 'Error fetching session data. Please try again later.'
        return jsonify ({'alert_type': 'error', 'message':'Error fetching session data. Please try again later.'})

#@sessions_bp.route('/uploaded_image/<filename>')
@sessions_bp.route('/uploaded_images/<filename>')
def display_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)




