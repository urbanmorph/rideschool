
print("logins.py")

from altmo_utils.db import get_db_cursor
import bcrypt
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, current_app

#from .config.config import get_config_value 

from .forms import YourLoginForm  # Import the login form 

import traceback
from flask import current_app
logins_bp = Blueprint('logins', __name__)



@logins_bp.route('/logins', methods=['GET'])
def index():
    form = YourLoginForm()  # Creates an instance of the login form
    return render_template('logins.html', form=form)



@logins_bp.route('/check_logins', methods=['POST'])
def check_logins():
    db_cursor = None
    form = YourLoginForm(request.form)  # Creates an instance of the login form
    try:
        with get_db_cursor(commit=True) as db_cursor:
            contact = request.form['contact']
            user_password = request.form['password']       
                 
            role = None
            if contact == str(current_app.config['ADMIN_CONTACT']) and user_password == current_app.config['ADMIN_PASSWORD']:

                # Admin login: If the contact and password match, set the session as an admin
                session['logged_in'] = True
                session['role'] = 'admin'
                return render_template('admin_display.html', role='admin')

            db_cursor.execute("SELECT * FROM users_signup WHERE contact_no=%s", (contact,))
            user_data = db_cursor.fetchone()
            
            if user_data:                
                #hashed_password = user_data.get('hashed_password')
                hashed_password = user_data.get('password')
              
                if bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8')):
                    role = user_data['role'] 

                # trainer and participant login.
                if role == 'trainer':
                    # Fetch trainer details from the trainers table using contact number
                    db_cursor.execute("SELECT id, name, status FROM trainer WHERE contact=%s", (contact,))
                    trainer_data = db_cursor.fetchone()

                    if trainer_data:
                        
                        id = trainer_data['id']
                        name = trainer_data['name']
                        status = trainer_data['status']
                        session['trainer_name'] = name

                        if status == 'CERTIFIED':
                            session['logged_in'] = True
                            session['role'] = role
                            session['trainer_id'] = id
                            session['trainer_name'] = name
 
                            # Fetch training_location_id based on the logged-in trainer's trainer_id
                            db_cursor.execute("SELECT t_location_id FROM trainer WHERE id=%s", (id,))
                            training_location_id = db_cursor.fetchone()['t_location_id']

                            # Fetch participant data based on the training_location_id
                            db_cursor.execute("SELECT id, name, contact, status FROM participants WHERE t_location_id=%s AND (status='ONGOING' OR status='NEW')", (training_location_id,))
                            participant_data = db_cursor.fetchall()

                            # Commit the transaction if everything is successful
                            return render_template('trainer_details.html', role=role, trainer_name=name, participants=participant_data)
                        else:
                            ##return "Trainer is not certified. Please complete your certification."
                            error_message = "Incorrect contact number or password"
                            return render_template('logins.html', form=form, error_message=error_message)
                elif role == 'participant':
                    # Fetch participant details from the participants table using contact number
                    db_cursor.execute("SELECT id, name, status, t_location_id FROM participants WHERE contact=%s", (contact,))
                    participant_data = db_cursor.fetchone()

                    if participant_data:
                        session['logged_in'] = True
                        session['role'] = role                        
                        session['participant_id'] = participant_data['id']
                        session['participant_name'] = participant_data['name']
                        session['participant_status'] = participant_data['status']                  
                        training_location_id = participant_data['t_location_id']
                        print("status:",session['participant_status'])
                        db_cursor.execute("SELECT address FROM training_locations_list WHERE id = %s", (training_location_id,))
                        training_location_address = db_cursor.fetchone()

                        if training_location_address:
                            training_location_address = training_location_address['address']
                            session['participant_training_location'] = training_location_address
                        else:
                            print("Training Location Address not found in the database")

                        db_cursor.execute("""
                            SELECT 
                                COALESCE(s.actual_date, '1970-01-01'::timestamp) AS actual_datetime, 
                                COALESCE(s.picture_path, '') AS picture_path, 
                                COALESCE(s.video_path, '') AS video_path,
                                t.name, 
                                t.contact, 
                                tl.address
                            FROM 
                                participants p
                            LEFT JOIN sessions s ON p.id = s.participant_id
                            LEFT JOIN trainer t ON t.t_location_id = p.t_location_id
                            INNER JOIN training_locations_list tl ON tl.id = p.t_location_id
                            WHERE 
                                p.id = %s;                        
                        """, (session['participant_id'],))

                        session_trainer_data = db_cursor.fetchall()

                        if session_trainer_data:
                            session['session_trainer_data'] = session_trainer_data

                            return render_template('participant_display.html', role=role)
                        else:                            
                            error_message = "Incorrect contact number or password."
                            return render_template('logins.html', form=form, error_message=error_message)                    
                    else:
                        error_message = "Participant details not found"
                        return render_template('logins.html', form=form, error_message=error_message)    
                else:
                    ##return "Incorrect contact no or password"
                    error_message = "Incorrect contact number or password. please check your credentials and try again "
                    return render_template('logins.html', form=form, error_message=error_message)
            else:
                error_message = "Please create an account"
                return render_template('logins.html', form=form, error_message=error_message)
                #return render_template('logins.html', form=form, error_message=error_message)    
    except Exception as e:
        traceback.print_exc()
        print("An error occurred during database query:", str(e))    
        error_message = f"An error occurred: {str(e)}"
        return render_template('logins.html', form=form, error_message=error_message)

    #finally:
     #   pass
        
    # If none of the conditions are met, return a generic error response
    #return "An error occurred during login."

@logins_bp.route('/update_participant_statuses', methods=['POST'])
def update_participant_statuses():
    db_cursor = None
    try:
        updates = request.get_json()        
        with get_db_cursor(commit=True) as db_cursor:
           
            for update in updates:
                participant_id = update.get('participantId')
                new_status = update.get('newStatus')
                try:
                    participant_id = int(participant_id)
                except ValueError:
                    return f"Invalid participant ID: {update.get('participantId')}"

                ###db_cursor.execute("UPDATE participants SET participant_status = %s, training_end_date = CURRENT_TIMESTAMP WHERE participant_id = %s", (new_status, participant_id))
                # Update only the specific participant_id
                db_cursor.execute(
                 #"UPDATE participants SET participant_status = %s WHERE participant_id = %s",
                "UPDATE participants SET status = %s WHERE id = %s",
                (new_status, participant_id)
                    )

                # Update training_end_date only if the new_status is "completed"
                if new_status == "COMPLETED":
                    db_cursor.execute(
                    # "UPDATE participants SET training_end_date = CURRENT_TIMESTAMP WHERE participant_id = %s",
                    "UPDATE participants SET training_end = CURRENT_TIMESTAMP WHERE id = %s",
                    (participant_id,)
                     )


            return jsonify({"success": True, "participantId": participant_id, "newStatus": new_status})

    except Exception as e:
        traceback.print_exc
        current_app.logger.error("An error occurred during database update: %s", str(e))

        return jsonify({"success": False, "error": "An error occurred. Please check the logs for more information."})
    finally:
        pass

@logins_bp.route('/logout', methods=['POST'])
def logout():
    role = session.get('role')
    if role == 'participant':
        session.pop('participant_id', None)
        session.pop('participant_name', None)
        session.pop('role', None)
    elif role == 'trainer':
        session.pop('trainer_id', None)
        session.pop('trainer_name', None)
        session.pop('role', None)
    elif role == 'admin':
        session['role'] = None
        if role is None and session.get('contact') is None:
            session.clear()
            return "Logged out successfully."

    return redirect(url_for('logins.index'))

@logins_bp.route('/trainer_details')
def trainer_details():
    role = session.get('role')
    form = YourLoginForm() # reusing the instance created in /check_logins
    if role != 'trainer':
        return redirect(url_for('logins.index'))

    try:
        with get_db_cursor(commit=False) as db_cursor: 
            trainer_id = session.get('trainer_id')

            db_cursor.execute("SELECT name, status FROM trainer WHERE id = %s", (trainer_id,))
            trainer_data = db_cursor.fetchone()

            if trainer_data:
                trainer_name, trainer_status = trainer_data

                db_cursor.execute("SELECT id, name, contact, status FROM participants WHERE t_location_id = (SELECT t_location_id FROM trainer WHERE id = %s) AND (status = 'ONGOING' OR status = 'NEW')", (trainer_id,))
                participant_data = db_cursor.fetchall()

                valid_status_values = [status[0] for status in db_cursor.fetchall()]

                return render_template('trainer_details.html', role=role, trainer_name=trainer_name, participants=participant_data, valid_status_values=valid_status_values)
            else:                
                ##return render_template('logins.html', form=form, error_message=error_message)
                error_message = "Trainer details not found."
                return render_template('logins.html', form=form, error_message=error_message)

    except Exception as e:
        traceback.print_exc()
        print("An error occurred during trainer details retrieval:", str(e))
        return f"An error occurred: {str(e)}"
   
@logins_bp.route('/participants-display')
def participants_display():
    role = session.get('role')
    if role != 'participant':
        return redirect(url_for('logins.index'))

    db_cursor = None
    error_message = None

    try:
        with get_db_cursor(commit=False) as db_cursor:       
            participant_id = session.get('participant_id')
            db_cursor.execute("""
                SELECT 
                    COALESCE(s.actual_date, 0) AS actual_datetime, 
                    COALESCE(s.picture_path, 0) AS picture_path, 
                    COALESCE(s.video_path, 0) AS video_path,
                    t.name, 
                    t.contact, 
                    tl.address
                FROM 
                    participants p
                LEFT JOIN sessions s ON p.id = s.participant_id
                LEFT JOIN trainer t ON t.t_location_id = p.t_location_id
                INNER JOIN training_locations_list tl ON tl.id = p.t_location_id
                WHERE 
                    p.id = %s;
            """, (participant_id,))

            session_trainer_data = db_cursor.fetchall()

            if session_trainer_data:
                session['session_trainer_data'] = session_trainer_data

            else:
                error_message = "Participant details not found."

    except Exception as e:
        print("An error occurred during participant display:", str(e))
        error_message = "An error occurred during participant display."

    return render_template('participant_display.html', role=role, error_message=error_message)



@logins_bp.route('/admin-display')
def admin_display():
    role = session.get('role')
    if role != 'admin':
        return redirect(url_for('logins.index'))
    return render_template('admin_display.html', role=role)
