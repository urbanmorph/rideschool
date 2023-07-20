from flask import Blueprint, render_template, request, send_from_directory, jsonify, current_app
import os
import psycopg2
import logging
from datetime import datetime

sessions_bp = Blueprint('sessions', __name__)

# Create a database connection
def get_db_connection():
    conn = psycopg2.connect(
        host='127.0.0.1',
        port='5432',
        database='Pedal_Shaale',
        user='postgres',
        password='root'
    )
    conn.set_session(autocommit=True)
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop the sessions table if it exists
    cursor.execute('DROP TABLE IF EXISTS sessions')

    # Create the sessions table with the necessary columns
    cursor.execute('''
        CREATE TABLE sessions (
            id SERIAL PRIMARY KEY,
            participant_name TEXT,
            trainer_name TEXT,
            scheduled_datetime TIMESTAMP,
            actual_datetime TIMESTAMP,
            hours_trained FLOAT,
            picture_path TEXT,
            video_path TEXT,
            description TEXT,
            session_current_date TIMESTAMP DEFAULT current_timestamp,
            session_update_date TIMESTAMP DEFAULT current_timestamp
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

# Initialize the database if it does not exist
def create_database():
    conn = psycopg2.connect(
        host='127.0.0.1',
        port='5432',
        database='Pedal_Shaale',
        user='postgres',
        password='root'
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
    # Fetch the trainer names from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT trainer_id, trainer_name FROM trainer")
    trainers = [{'trainer_id': row[0], 'trainer_name': row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('sessions_form.html', trainers=trainers)

@sessions_bp.route('/trainers')
def get_trainers():
    try:
        # Fetch the trainer names from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT trainer_id, trainer_name FROM trainer")
        trainers = [{'trainer_id': row[0], 'trainer_name': row[1]} for row in cursor.fetchall()]
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
        # Fetch the training_location_id for the selected trainer
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT training_location_id FROM trainer WHERE trainer_id = %s", (trainer_id,))
        result = cursor.fetchone()

        if result is None:
            return jsonify([])  # Return empty list if no training_location_id found

        training_location_id = result[0]

        # Fetch the participants based on the matching training_location_id, participant_status as "NEW" or "ONGOING",
        # and exclude those with participant_status as "COMPLETED"
        cursor.execute(
            "SELECT participant_name, training_location_id FROM participants WHERE training_location_id = %s AND participant_status IN ('NEW', 'ONGOING') AND participant_name NOT IN (SELECT participant_name FROM participants WHERE participant_status = 'COMPLETED')",
            (training_location_id,))
        participants = [{'participant_name': row[0], 'training_location_id': row[1]} for row in cursor.fetchall()]
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
        participant_name = request.form['participant-name']
        trainer_name = request.form['trainer-name']
        scheduled_datetime = request.form['scheduled-datetime']
        actual_datetime = request.form['actual-datetime']
        hours_trained = request.form['hours-trained']
        picture = request.files['session-picture']
        video = request.files['session-video']
        description = request.form['session-description']

        # Save the image and video files to the uploaded_image folder under the static folder
        picture_filename = picture.filename
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)
        picture.save(os.path.join(current_app.root_path, picture_path))

        video_filename = video.filename
        video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video_filename)
        video.save(os.path.join(current_app.root_path, video_path))

        # Insert the data into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (
                participant_name, 
                trainer_name, 
                scheduled_datetime, 
                actual_datetime, 
                hours_trained, 
                picture_path, 
                video_path, 
                description
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (participant_name, trainer_name, scheduled_datetime, actual_datetime, hours_trained,
              picture_path, video_path, description))
        conn.commit()
        cursor.close()
        conn.close()

        return 'Form submitted successfully!'
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return 'Error submitting the form. Please try again later.'

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
