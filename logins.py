# Import required modules at the top of your Flask application
import bcrypt
import psycopg2
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, current_app

logins_bp = Blueprint('logins', __name__)

# Initialize db_connection to None initially
db_connection = None

def get_db_connection():
    global db_connection
    if db_connection is None:
        # PostgreSQL database connection
        db_connection = psycopg2.connect(
            host='127.0.0.1',
            database='Pedal_Shaale',
            user='postgres',
            password='root'
        )
    return db_connection

@logins_bp.route('/logins')
def index():
    return render_template('logins.html')

@logins_bp.route('/check_logins', methods=['POST'])
def check_logins():
    db_cursor = None
    try:
        db_connection = get_db_connection()
        db_cursor = db_connection.cursor()

        contact = request.form['contact']
        user_password = request.form['password']

        # Debugging: Log the received form data
        print("Received form data - Contact:", contact)
        print("Received form data - Password:", user_password)

        db_cursor.execute("SELECT * FROM users_signup WHERE contact_no=%s", (contact,))
        user_data = db_cursor.fetchone()
        print("User Data:", user_data) 

        if user_data:
            hashed_password = user_data[2]

            if bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8')):
                role = user_data[3]

                if role == 'trainer':
                    # Fetch trainer details from the trainers table using contact number
                    db_cursor.execute("SELECT trainer_id, trainer_name, trainer_status FROM trainer WHERE trainer_contact=%s", (contact,))
                    trainer_data = db_cursor.fetchone()

                    if trainer_data:
                        trainer_id, trainer_name, trainer_status = trainer_data

                        session['trainer_name'] = trainer_name

                        if trainer_status == 'CERTIFIED':
                            session['logged_in'] = True
                            session['role'] = role
                            session['trainer_id'] = trainer_id
                            session['trainer_name'] = trainer_name

                            # Fetch training_location_id based on the logged-in trainer's trainer_id
                            db_cursor.execute("SELECT training_location_id FROM trainer WHERE trainer_id=%s", (trainer_id,))
                            training_location_id = db_cursor.fetchone()[0]

                            # Fetch participant data based on the training_location_id
                            db_cursor.execute("SELECT participant_id, participant_name, participant_contact, participant_status FROM participants WHERE training_location_id=%s AND (participant_status='ONGOING' OR participant_status='NEW')", (training_location_id,))
                            participant_data = db_cursor.fetchall()
                            
                            # Commit the transaction if everything is successful
                            db_connection.commit()
                            return render_template('trainer_details.html', role=role, trainer_name=trainer_name, participants=participant_data)
                        else:
                            return "Trainer is not certified. Please complete your certification."

                elif role == 'participant':
                    # Fetch participant details from the participants table using contact number
                    db_cursor.execute("SELECT participant_id, participant_name, participant_status, training_location_id FROM participants WHERE participant_contact=%s", (contact,))
                    participant_data = db_cursor.fetchone()

                    if participant_data:
                        session['logged_in'] = True
                        session['role'] = role
                        session['participant_id'] = participant_data[0]
                        session['participant_name'] = participant_data[1]
                        session['participant_status'] = participant_data[2]

                        training_location_id = participant_data[3]

                        db_cursor.execute("SELECT training_location_address FROM training_locations_list WHERE training_location_id = %s", (training_location_id,))
                        training_location_address = db_cursor.fetchone()

                        if training_location_address:
                            training_location_address = training_location_address[0]
                            session['participant_training_location'] = training_location_address
                        else:
                            print("Training Location Address not found in the database")

                        db_cursor.execute("""
                            SELECT 
    COALESCE(s.actual_datetime, '1970-01-01'::timestamp) AS actual_datetime, 
    COALESCE(s.picture_path, '') AS picture_path, 
    COALESCE(s.video_path, '') AS video_path,
    t.trainer_name, 
    t.trainer_contact, 
    tl.training_location_address
FROM 
    participants p
LEFT JOIN sessions s ON p.participant_id = s.participant_id
LEFT JOIN trainer t ON t.training_location_id = p.training_location_id
INNER JOIN training_locations_list tl ON tl.training_location_id = p.training_location_id
WHERE 
    p.participant_id = %s;

                        """, (session['participant_id'],))

                        session_trainer_data = db_cursor.fetchall()

                        if session_trainer_data:
                            session['session_trainer_data'] = session_trainer_data

                            return render_template('participant_display.html', role=role)
                        else:
                            return "Incorrect contact no or password"
                    else:
                        return "Participant details not found."
                    
                

                elif role == 'admin' and contact == '9999999999':
                    session['logged_in'] = True
                    session['role'] = role
                    return render_template('admin_display.html', role=role)
                else:
                    return "Invalid role."
            else:
                return "Incorrect password."

    except Exception as e:
        print("An error occurred during database query:", str(e))

        # Roll back the transaction to undo any changes made before the error
        db_connection.rollback()


        return f"An error occurred: {str(e)}"
    finally:
        if db_cursor is not None:
            db_cursor.close()

@logins_bp.route('/update_participant_statuses', methods=['POST'])
def update_participant_statuses():
    try:
        updates = request.get_json()
        db_cursor = get_db_connection().cursor()

        for update in updates:
            participant_id = update.get('participantId')
            new_status = update.get('newStatus')

            try:
                participant_id = int(participant_id)
            except ValueError:
                return f"Invalid participant ID: {update.get('participantId')}"

            db_cursor.execute("UPDATE participants SET participant_status = %s WHERE participant_id = %s", (new_status, participant_id))

        db_connection.commit()

        return jsonify({"success": True, "participantId": participant_id, "newStatus": new_status})

    except Exception as e:
        current_app.logger.error("An error occurred during database update: %s", str(e))
        db_connection.rollback()

        return jsonify({"success": False, "error": "An error occurred. Please check the logs for more information."})
    finally:
        if db_cursor is not None:
            db_cursor.close()

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
    if role != 'trainer':
        return redirect(url_for('logins.index'))

    try:
        db_connection = get_db_connection()
        db_cursor = db_connection.cursor()

        trainer_id = session.get('trainer_id')

        db_cursor.execute("SELECT trainer_name, trainer_status FROM trainer WHERE trainer_id = %s", (trainer_id,))
        trainer_data = db_cursor.fetchone()

        if trainer_data:
            trainer_name, trainer_status = trainer_data

            db_cursor.execute("SELECT participant_id, participant_name, participant_contact, participant_status FROM participants WHERE training_location_id = (SELECT training_location_id FROM trainer WHERE trainer_id = %s) AND (participant_status = 'ONGOING' OR participant_status = 'NEW')", (trainer_id,))
            participant_data = db_cursor.fetchall()

            valid_status_values = [status[0] for status in db_cursor.fetchall()]

            return render_template('trainer_details.html', role=role, trainer_name=trainer_name, participants=participant_data, valid_status_values=valid_status_values)
        else:
            return "Trainer details not found."

    except Exception as e:
        print("An error occurred during trainer details retrieval:", str(e))
        return f"An error occurred: {str(e)}"
    finally:
        if db_cursor is not None:
            db_cursor.close()

# ... Existing code ...

@logins_bp.route('/participants-display')
def participants_display():
    role = session.get('role')
    if role != 'participant':
        return redirect(url_for('logins.index'))

    db_cursor = None
    error_message = None

    try:
        db_connection = get_db_connection()
        db_cursor = db_connection.cursor()

        participant_id = session.get('participant_id')
        db_cursor.execute("""
            SELECT 
                COALESCE(s.actual_datetime, 0) AS actual_datetime, 
                COALESCE(s.picture_path, 0) AS picture_path, 
                COALESCE(s.video_path, 0) AS video_path,
                t.trainer_name, 
                t.trainer_contact, 
                tl.training_location_address
            FROM 
                participants p
            LEFT JOIN sessions s ON p.participant_id = s.participant_id
            LEFT JOIN trainer t ON t.training_location_id = p.training_location_id
            INNER JOIN training_locations_list tl ON tl.training_location_id = p.training_location_id
            WHERE 
                p.participant_id = %s;
        """, (participant_id,))

        session_trainer_data = db_cursor.fetchall()

        if session_trainer_data:
            session['session_trainer_data'] = session_trainer_data

        else:
            error_message = "Participant details not found."

    except Exception as e:
        print("An error occurred during participant display:", str(e))
        error_message = "An error occurred during participant display."

    finally:
        if db_cursor is not None:
            db_cursor.close()

    return render_template('participant_display.html', role=role, error_message=error_message)
