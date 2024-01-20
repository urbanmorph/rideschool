  # admin.py
print("import feane/ admin.py")
from flask import Blueprint, render_template, request, jsonify, current_app
import logging # Import the logging module
from altmo_utils.db import get_db_cursor
import traceback 
admin_bp = Blueprint('admin', __name__)
#
@admin_bp.route('/admin')
def admin_home():
    return 'Admin Page'

# Route to display participant information for all participants
@admin_bp.route('/participant-info', methods=['GET'])
def participant_info():
    try:
        with get_db_cursor() as cursor:        
            cursor.execute("""
                SELECT
                    p.participant_id,
                    p.participant_name,
                    p.participant_email,
                    p.participant_contact,
                    tl.training_location,
                    tl.training_location_address,
                    p.participant_status,
                    p.participant_created_at,
                    p.participant_code
                FROM participants p
                JOIN training_locations_list tl ON p.training_location_id = tl.training_location_id
            """)
            participants = cursor.fetchall()
            print(participants)

        # Render the participant_info.html template with the list of participants
        return render_template('participant_info.html', participants=participants)
    except Exception as e:
        traceback.print_exc()
        return f"Error: {str(e)}"

# Route to display trainer information for all trainers
@admin_bp.route('/trainer-info', methods=['GET'])
def trainer_info():
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.trainer_id,
                    t.trainer_name,
                    t.trainer_email,
                    t.trainer_contact,
                    CASE WHEN t.training_location_id = 0 THEN NULL
                         ELSE tl.training_location
                    END AS training_location,      
                    t.trainer_address,
                    t.trainer_gender,
                    t.trainer_aadhar_no,
                    t.trainer_created_at,
                    t.trainer_training_completion_date,
                    o.organisation_name,
                    t.trainer_status,
                    t.trainer_code
                FROM trainer t
                LEFT JOIN training_locations_list tl ON t.training_location_id = tl.training_location_id
                JOIN organisation o ON t.organisation_id = o.organisation_id
            """)
            trainers = cursor.fetchall()

        # Fetch the list of training locations for the dropdown
        with get_db_cursor() as cursor:
            cursor.execute("SELECT training_location_id, training_location FROM training_locations_list")
            training_locations = cursor.fetchall()
            print(training_locations )

        # Render the trainer_info.html template with the list of trainers and training locations
        return render_template('trainer_info.html', trainers=trainers, training_locations=training_locations)
    except Exception as e:
        traceback.print_exc()
        return f"Error: {str(e)}"

#adin session 
@admin_bp.route('/sessions_info')
def sessions_info():
    print("Reached sessions_info route")  # Debugging statement
    try:
         # Create a database connection
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.trainer_id,  
                    t.trainer_name,
                    p.participant_name,
                    p.training_start_date,
                    p.training_end_date,
                    s.actual_datetime,
                    s.hours_trained,
                    s.picture_path,
                    s.video_path,
                    s.description,
                    s.session_update_date,
                    p.participant_id
                FROM sessions s
                JOIN trainer t ON s.trainer_id = t.trainer_id
                JOIN participants p ON s.participant_id = p.participant_id
                
               ;                
            """)
            sessions = cursor.fetchall()
        return render_template('sessions_info.html', sessions=sessions)   
    except Exception as e:
        traceback.print_exc()
        return f"Error:{str(e)}"     
               
@admin_bp.route('/trainer_details/<int:trainer_id>')
def trainer_details(trainer_id):
    try:
        # Convert trainer_id to an integer
        trainer_id = int(trainer_id)

        # Fetch trainer details based on trainer_id from the database
        with get_db_cursor() as cursor:
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
                LEFT JOIN sessions s ON t.trainer_id = s.trainer_id
                LEFT JOIN training_locations_list tl ON t.training_location_id = tl.training_location_id
                LEFT JOIN organisation o ON t.organisation_id = o.organisation_id
                WHERE t.trainer_id = %s
                GROUP BY t.trainer_id, tl.training_location_address, o.organisation_name
            """, (trainer_id,))                    
            trainer_data = cursor.fetchone()

        if trainer_data:
            return render_template('trainer_admin.html', **trainer_data)

    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching trainer details. Please try again later.'
    
# Helper function to fetch feedback data for a specific participant with COMPLETED or CERTIFIED status
def fetch_feedback_data(participant_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM feedback WHERE participant_id = %s", (participant_id,))
            feedback_data = cursor.fetchall()

            return feedback_data
    except Exception as e:
        traceback.print_exce()
        logging.error("An error occurred while fetching feedback data:", exc_info=True)
        return None

@admin_bp.route('/participant_admin/<int:participant_id>')
def participant_admin(participant_id):
    try:
        # Fetch participant details based on participant_id from the database
        with get_db_cursor() as cursor:
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
                LEFT JOIN sessions s ON p.participant_id = s.participant_id
                LEFT JOIN training_locations_list tl ON p.training_location_id = tl.training_location_id
                WHERE p.participant_id = %s
                GROUP BY p.participant_id, p.participant_name, p.participant_email, p.participant_contact, p.participant_age, p.participant_gender, p.participant_address, tl.training_location_address, p.participant_created_at, p.participant_status, p.participant_code
            """, (participant_id,))

            participant_data = cursor.fetchone()
            print(participant_data)
        feedback_data = None

        if participant_data:
            
        # Check if the participant's status is "COMPLETED" or "CERTIFIED"
           # if participant_status in ['COMPLETED', 'CERTIFIED']:
           if participant_data['participant_status'] in ['COMPLETED', 'CERTIFIED']:
            # Fetch feedback data only for the specific participant with "COMPLETED" or "CERTIFIED" status
                feedback_data = fetch_feedback_data(participant_id)
        else:
            feedback_data = None
        return render_template('participant_admin.html', participant_data=participant_data, feedback_data=feedback_data)
    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching participant details. Please try again later.'
    

    
@admin_bp.route('/update_participant_statuses_admin', methods=['POST'])
def update_participant_statuses_admin():
    try:
        updates = request.get_json()
        success = True
        error_message = None

        # Debugging: Print the received updates
        print("Received updates:", updates)
        with get_db_cursor(commit=True) as cursor:
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
                cursor.execute("UPDATE participants SET participant_status = %s WHERE participant_id = %s", (new_status, participant_id))

            if success:
                return jsonify({"success": True})
            else:                
                return jsonify({"success": False, "error": error_message})

    except Exception as e:
        current_app.logger.error("Error in /update_participant_statuses_admin: %s", str(e))
        traceback.print_exc()
        # Debugging: Print the error message
        print("Error in /update_participant_statuses_admin:", str(e))
        return jsonify({"success": False, "error": "An error occurred. Please check the logs for more information."})

@admin_bp.route('/trainer_update_status', methods=['POST'])
def update_trainer_status():
   
    try:
        data = request.get_json()
        trainer_id = data.get('trainerId')
        new_status = data.get('newStatus')
        new_location_id = data.get('newLocationId')
        
        with get_db_cursor(commit=True) as cursor:       
            cursor.execute("UPDATE trainer SET trainer_status = %s WHERE trainer_id = %s", (new_status, trainer_id))
             # Update the training_location_id in the trainers table
            cursor.execute("UPDATE trainer SET training_location_id = %s WHERE trainer_id = %s", (new_location_id, trainer_id))            
        return jsonify({"success": True})
    except Exception as e:
        current_app.logger.error("Error updating trainer status:", exc_info=True)
        return jsonify({"success": False, "error": str(e)})
   
@admin_bp.route('/organisation-info', methods=['GET'])
def organisation_info():
    try:
        with get_db_cursor() as cursor:
        
            cursor.execute("""
                SELECT
                    organisation_id,
                    organisation_name,
                    organisation_address,
                    organisation_contact,
                    organisation_email,
                    organisation_type,
                    organisation_activities,
                    organisation_legal_status_document,
                    coordinator_name,
                    coordinator_email,
                    coordinator_contact,
                    organisation_created_at
                    
                FROM organisation
            """)
            organizations = cursor.fetchall()
        ###
        # loops through organizations and print the organisation_legal_status_document path this is just for debugging 
        for organization in organizations:
            legal_status_document_path = organization['organisation_legal_status_document']
            print("Organisation Document Path:", legal_status_document_path)
        #print("organization:", organization['organisation_legal_status_document'])
        ###
        #print("Organizations:", organizations)  # Debugging: Print fetched data
            
        return render_template('organization_admin.html', organizations=organizations)
    except Exception as e:
        traceback.print_exc()
        print("Error:", str(e))  
        return f"Error: {str(e)}"
