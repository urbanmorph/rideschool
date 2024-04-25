  # admin.py
print("import feane/ admin.py")
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
import logging # Import the logging module
from altmo_utils.db import get_db_cursor
import traceback 
from functools import wraps
admin_bp = Blueprint('admin', __name__)

def admin_required(route_func):
    @wraps(route_func)
    def decorated_route(*args, **kwargs):
        if session.get('role') != 'admin': 
            error_message = 'Please login as a valid user to view this page.'
            return redirect(url_for('logins.index', error_message=error_message))
        return route_func(*args, **kwargs)
    return decorated_route


@admin_bp.route('/admin')
@admin_required
def admin_home():
    return 'Admin Page'

# Route to display participant information for all participants
@admin_bp.route('/participant-info', methods=['GET'])
@admin_required
def participant_info():
    try:
        with get_db_cursor() as cursor:        
            cursor.execute("""
                SELECT
                    p.id,
                    p.name,
                    p.email,
                    p.contact,
                    tl.training_location,
                    tl.address,
                    p.status,
                    p.created_date,                    
                    p.code
                FROM participants p
                JOIN training_locations_list tl ON p.t_location_id = tl.id
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
@admin_required
def trainer_info():
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.id,
                    t.name,
                    t.email,
                    t.contact,
                    CASE WHEN t.t_location_id = 0 THEN NULL
                         ELSE tl.training_location
                    END AS training_location,      
                    t.address,
                    t.gender,
                    t.aadhar_no,
                    t.created_date,
                    t.training_completion,
                    o.name AS organization_name, -- rename this o.name to this organization_name to avoide confusion 
                    t.status,
                    t.code
                FROM trainer t
                LEFT JOIN training_locations_list tl ON t.t_location_id = tl.id
                JOIN organisation o ON t.org_id = o.id
            """)
            trainers = cursor.fetchall()

        # Fetch the list of training locations for the dropdown
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, training_location FROM training_locations_list")
            training_locations = cursor.fetchall()
            print(training_locations )

        # Render the trainer_info.html template with the list of trainers and training locations
        return render_template('trainer_info.html', trainers=trainers, training_locations=training_locations)
    except Exception as e:
        traceback.print_exc()
        return f"Error: {str(e)}"

#admin session 
@admin_bp.route('/sessions_info')
@admin_required
def sessions_info():
    print("Reached sessions_info route")  
    try:
         # Creating a database connection
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.id,  
                    t.name,
                    p.name AS participant_name,
                    p.training_start,
                    p.training_end,
                    s.actual_date,
                    s.hours_trained,
                    s.picture_path,
                    s.video_path,
                    s.description,
                    s.update_date,
                    p.id
                FROM sessions s
                JOIN trainer t ON s.trainer_id = t.id
                JOIN participants p ON s.participant_id = p.id
                
               ;                
            """)
            sessions = cursor.fetchall()
        return render_template('sessions_info.html', sessions=sessions)   
    except Exception as e:
        traceback.print_exc()
        return f"Error:{str(e)}"     
               
@admin_bp.route('/trainer_details/<int:id>')
@admin_required
def trainer_details(id):
    try:
        # Converts trainer_id to an integer
        trainer_id = int(id)

        # Fetch trainer details based on trainer_id from the database
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.id,
                    t.name,
                    t.email,
                    t.contact,
                    tl.address AS training_loaction_address,
                    t.address,
                    t.gender,
                    t.aadhar_no,
                    t.created_date,
                    t.training_completion,
                    o.name AS organisation_name,
                    t.status,
                    t.code,
                    SUM(s.hours_trained) AS total_hours_trained,  -- Calculate the total hours trained
                    COUNT(s.hours_trained) AS session_count  -- Calculate the count of sessions
                FROM trainer t
                LEFT JOIN sessions s ON t.id = s.trainer_id
                LEFT JOIN training_locations_list tl ON t.t_location_id = tl.id
                LEFT JOIN organisation o ON t.org_id = o.id
                WHERE t.id = %s
                GROUP BY t.id, tl.address, o.name
            """, (trainer_id,))                    
            trainer_data = cursor.fetchone()

        if trainer_data:
            return render_template('trainer_admin.html', **trainer_data)

    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        #return 'Error fetching trainer details. Please try again later.'
        return f"Error fetching trainer details. Details: {str(e)}"
    
# function to fetch feedback data for a specific participant with COMPLETED or CERTIFIED status
def fetch_feedback_data(participant_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM feedback WHERE id = %s", (participant_id,))
            feedback_data = cursor.fetchall()

            return feedback_data
    except Exception as e:
        traceback.print_exce()
        logging.error("An error occurred while fetching feedback data:", exc_info=True)
        return None

@admin_bp.route('/participant_admin/<int:id>')
@admin_required
def participant_admin(id):
    try:
        # Fetch participant details based on participant_id from the database
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    p.id,
                    p.name,
                    p.email,
                    p.contact,
                    p.age,
                    p.gender,
                    p.address,
                    tl.address AS training_location_addres,
                    p.created_date,
                    p.status,
                    p.code,
                    SUM(s.hours_trained) AS total_hours_trained,
                    COUNT(s.hours_trained) AS session_count
                FROM participants p
                LEFT JOIN sessions s ON p.id = s.participant_id
                LEFT JOIN training_locations_list tl ON p.t_location_id = tl.id
                WHERE p.id = %s
                GROUP BY p.id, p.name, p.email, p.contact, p.age, p.gender, p.address, tl.address, p.created_date, p.status, p.code
            """, (id,))

            participant_data = cursor.fetchone()
            print(participant_data)
        feedback_data = None

        if participant_data:
            
        # Check if the participant's status is "COMPLETED" or "CERTIFIED"
           # if participant_status in ['COMPLETED', 'CERTIFIED']:
           if participant_data['status'] in ['COMPLETED', 'CERTIFIED']:
            # Fetch feedback data only for the specific participant with "COMPLETED" or "CERTIFIED" status
                feedback_data = fetch_feedback_data(id)
        else:
            feedback_data = None
        return render_template('participant_admin.html', participant_data=participant_data, feedback_data=feedback_data)
    except Exception as e:
        traceback.print_exc()
        logging.error("An error occurred:", exc_info=True)
        return 'Error fetching participant details. Please try again later.'
    

    
@admin_bp.route('/update_participant_statuses_admin', methods=['POST'])
@admin_required
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
                cursor.execute("UPDATE participants SET status = %s WHERE id = %s", (new_status, participant_id))

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
@admin_required
def update_trainer_status():
   
    try:
        data = request.get_json()
        trainer_id = data.get('trainerId')
        new_status = data.get('newStatus')
        new_location_id = data.get('newLocationId')
        
        with get_db_cursor(commit=True) as cursor:       
            cursor.execute("UPDATE trainer SET status = %s WHERE id = %s", (new_status, trainer_id))
             # Update the training_location_id in the trainers table
            cursor.execute("UPDATE trainer SET t_location_id = %s WHERE id = %s", (new_location_id, trainer_id))            
        return jsonify({"success": True})
    except Exception as e:
        current_app.logger.error("Error updating trainer status:", exc_info=True)
        return jsonify({"success": False, "error": str(e)})
   
@admin_bp.route('/organisation-info', methods=['GET'])
@admin_required
def organisation_info():
    try:
        with get_db_cursor() as cursor:
        
            cursor.execute("""
                SELECT
                    id,
                    name,
                    address,
                    contact,
                    email,
                    org_type,
                    activities,
                    legal_document,
                    coordinator_name,
                    coordinator_email,
                    coordinator_contact,
                    created_date
                    
                FROM organisation
            """)
            organizations = cursor.fetchall()
        ###
        # loops through organizations and print the organisation_legal_status_document path this is just for debugging 
        for organization in organizations:
            legal_status_document_path = organization['legal_document']
            print("Organisation Document Path:", legal_status_document_path)
        #print("organization:", organization['organisation_legal_status_document'])
        ###
        #print("Organizations:", organizations)  
            
        return render_template('organization_admin.html', organizations=organizations)
    except Exception as e:
        traceback.print_exc()
        print("Error:", str(e))  
        return f"Error: {str(e)}"
