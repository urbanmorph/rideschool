# admin.py

from flask import Blueprint, render_template, request, jsonify, current_app
import psycopg2  # Import psycopg2 if you're using it for database connections
from config.config import get_config_value
import logging # Import the logging module


admin_bp = Blueprint('admin', __name__)
# Configure database connection
db_host = get_config_value('db_host')
db_user = get_config_value('db_user')
db_password = get_config_value('db_password')
db_name = get_config_value('db_name')



# Define the get_db_connection function in admin.py
def get_db_connection():
    return psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        dbname=db_name
    )

@admin_bp.route('/admin')
def admin_home():
    return 'Admin Page'



# Route to display participant information for all participants (moved from participant.py)
@admin_bp.route('/participant-info', methods=['GET'])
def participant_info():
    try:
        # You may need to add database connection parameters here, depending on your implementation
        # Connect to the database
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch participant details for all participants
        cursor.execute("""
            SELECT
                p.participant_id,
                p.participant_name,
                p.participant_email,
                p.participant_contact,
                tl.training_location_address,
                p.participant_status,
                p.participant_created_at,
                p.participant_code
            FROM participants p
            JOIN training_locations_list tl ON p.training_location_id = tl.training_location_id
        """)

        participants = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Render the participant_info.html template with the list of participants
        return render_template('participant_info.html', participants=participants)
    except Exception as e:
        return f"Error: {str(e)}"




# Route to display trainer information for all trainers
@admin_bp.route('/trainer-info', methods=['GET'])
def trainer_info():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch trainer details for all trainers
        cursor.execute("""
            SELECT
                t.trainer_id,
                t.trainer_name,
                t.trainer_email,
                t.trainer_contact,
                tl.training_location_address,
                t.trainer_address,
                t.trainer_gender,
                t.trainer_aadhar_no,
                t.trainer_created_at,
                t.trainer_training_completion_date,
                
                o.organisation_name,
               
                t.trainer_status,
                t.trainer_code
            FROM trainer t
            JOIN training_locations_list tl ON t.training_location_id = tl.training_location_id
            JOIN organisation o ON t.organisation_id = o.organisation_id
        """)

        trainers = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Render the trainer_info.html template with the list of trainers
        return render_template('trainer_info.html', trainers=trainers)
    except Exception as e:
        return f"Error: {str(e)}"




#adin session 
@admin_bp.route('/sessions_info')
def sessions_info():
    print("Reached sessions_info route")  # Debugging statement
    try:
         # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                t.trainer_id,  
                t.trainer_name,
                p.participant_name,
                s.actual_datetime,
                s.hours_trained,
                s.picture_path,
                s.video_path,
                s.description,
                s.session_current_date,
                p.participant_id
            FROM sessions s
            JOIN trainer t ON s.trainer_id = t.trainer_id
            JOIN participants p ON s.participant_id=p.participant_id ;
            """)
        sessions = cursor.fetchall()
        cursor.close()
        conn.close()   
        return render_template('sessions_info.html', sessions=sessions)   
    except Exception as e:
        return f"Error:{str(e)}"     
               
@admin_bp.route('/trainer_details/<int:trainer_id>')
def trainer_details(trainer_id):
    try:
        # Convert trainer_id to an integer
        trainer_id = int(trainer_id)

        # Fetch trainer details based on trainer_id from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                t.trainer_id,
                t.trainer_name,
                t.trainer_email,
                t.trainer_contact,
                tl.training_location_address,
                t.trainer_address,
                t.trainer_gender,
                t.trainer_aadhar_no,
                t.trainer_created_at,
                t.trainer_training_completion_date,
                o.organisation_name,
                t.trainer_status,
                t.trainer_code,
                SUM(s.hours_trained) AS total_hours_trained,  -- Calculate the total hours trained
                COUNT(s.hours_trained) AS session_count  -- Calculate the count of sessions
            FROM trainer t
            JOIN sessions s ON t.trainer_id = s.trainer_id
            LEFT JOIN training_locations_list tl ON t.training_location_id = tl.training_location_id
            LEFT JOIN organisation o ON t.organisation_id = o.organisation_id
            WHERE t.trainer_id = %s
            GROUP BY t.trainer_id, tl.training_location_address, o.organisation_name
        """, (trainer_id,))
        
        trainer_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if trainer_data:
            (   
                trainer_id,
                trainer_name,
                trainer_email,
                trainer_contact,
                training_location_address,
                trainer_address,
                trainer_gender,
                trainer_aadhar_no,
                trainer_created_at,
                trainer_training_completion_date,
                organisation_name,
                trainer_status,
                trainer_code,
                total_hours_trained,
                session_count 
            ) = trainer_data
        else:
            trainer_name = "Trainer Not Found"
            trainer_status = "N/A"

        return render_template(
            'trainer_admin.html',
            trainer_id=trainer_id,
            trainer_name=trainer_name,
            trainer_email=trainer_email,
            trainer_contact=trainer_contact,
            training_location_address=training_location_address,
            trainer_address=trainer_address,
            trainer_gender=trainer_gender,
            trainer_aadhar_no=trainer_aadhar_no,
            trainer_created_at=trainer_created_at,
            trainer_training_completion_date=trainer_training_completion_date,
            organisation_name=organisation_name,
            trainer_status=trainer_status,
            trainer_code=trainer_code,
            total_hours_trained=total_hours_trained,
            session_count =session_count 
        )

    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching trainer details. Please try again later.'
    



# Helper function to fetch feedback data for a specific participant with COMPLETED or CERTIFIED status
def fetch_feedback_data(participant_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback WHERE participant_id = %s", (participant_id,))
    feedback_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return feedback_data

    #participant admin 






@admin_bp.route('/participant_admin/<int:participant_id>')
def participant_admin(participant_id):
    try:
        # Fetch participant details based on participant_id from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.participant_id,
                p.participant_name,
                p.participant_email,
                p.participant_contact,
                p.participant_age,
                p.participant_gender,
                p.participant_address,
                tl.training_location_address,
                p.participant_created_at,
                p.participant_status,
                p.participant_code,
                SUM(s.hours_trained) AS total_hours_trained,
                COUNT(s.hours_trained) AS session_count
            FROM participants p
            JOIN sessions s ON p.participant_id = s.participant_id
            LEFT JOIN training_locations_list tl ON p.training_location_id = tl.training_location_id
            WHERE p.participant_id = %s
            GROUP BY p.participant_id, p.participant_name, p.participant_email, p.participant_contact, p.participant_age, p.participant_gender, p.participant_address, tl.training_location_address, p.participant_created_at, p.participant_status, p.participant_code
        """, (participant_id,))

        participant_data = cursor.fetchone()

        if participant_data:
            (
                participant_id,
                participant_name,
                participant_email,
                participant_contact,
                participant_age,
                participant_gender,
                participant_address,
                training_location_address,
                participant_created_at,
                participant_status,
                participant_code,
                total_hours_trained,
                session_count
            ) = participant_data

        # Check if the participant's status is "COMPLETED" or "CERTIFIED"
        if participant_status in ['COMPLETED', 'CERTIFIED']:
            # Fetch feedback data only for the specific participant with "COMPLETED" or "CERTIFIED" status
            feedback_data = fetch_feedback_data(participant_id)
        else:
            feedback_data = None

        cursor.close()
        conn.close()

        return render_template(
            'participant_admin.html',
            participant_id=participant_id,
            participant_name=participant_name,
            participant_email=participant_email,
            participant_contact=participant_contact,
            participant_age=participant_age,
            participant_gender=participant_gender,
            participant_address=participant_address,
            training_location_address=training_location_address,
            participant_created_at=participant_created_at,
            participant_status=participant_status,
            participant_code=participant_code,
            total_hours_trained=total_hours_trained,
            session_count=session_count,
            feedback_data=feedback_data
        )

    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching participant details. Please try again later.'

@admin_bp.route('/update_participant_statuses_admin', methods=['POST'])
def update_participant_statuses_admin():
    try:
        updates = request.get_json()
        db_cursor = get_db_connection().cursor()
        success = True
        error_message = None

        # Debugging: Print the received updates
        print("Received updates:", updates)

        for update in updates:
            participant_id = update.get('participantId')
            new_status = update.get('newStatus')

            try:
                participant_id = int(participant_id)
            except ValueError:
                success = False
                error_message = f"Invalid participant ID: {update.get('participantId')}"
                break  # Break the loop if an invalid ID is encountered

            # Update the participant status only if the ID is valid
            db_cursor.execute("UPDATE participants SET participant_status = %s WHERE participant_id = %s", (new_status, participant_id))

        if success:
            get_db_connection().commit()
            return jsonify({"success": True})
        else:
            get_db_connection().rollback()
            return jsonify({"success": False, "error": error_message})

    except Exception as e:
        current_app.logger.error("Error in /update_participant_statuses_admin: %s", str(e))

        # Debugging: Print the error message
        print("Error in /update_participant_statuses_admin:", str(e))

        get_db_connection().rollback()
        return jsonify({"success": False, "error": "An error occurred. Please check the logs for more information."})

    finally:
        if db_cursor is not None:
            db_cursor.close()
