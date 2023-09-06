# Import required modules at the top of your Flask application
import bcrypt
import psycopg2
from flask import Blueprint, render_template, request, session, redirect, url_for

logins_bp = Blueprint('logins', __name__)  # Fix the Blueprint constructor

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

@logins_bp.route('/logins')  # Change the route to /logins
def index():
    return render_template('logins.html')

@logins_bp.route('/check_logins', methods=['POST'])  # Change the route to /check_logins
def check_logins():
    db_cursor = None  # Initialize db_cursor to None
    try:
        db_connection = get_db_connection()  # Get or create a database connection
        db_cursor = db_connection.cursor()

        contact = request.form['contact']
        user_password = request.form['password']

        # Debugging: Log the received form data
        print("Received form data - Contact:", contact)
        print("Received form data - Password:", user_password)

        # Check if the contact is registered in the users_signup table
        db_cursor.execute("SELECT * FROM users_signup WHERE contact_no=%s", (contact,))
        user_data = db_cursor.fetchone()

        if user_data:
            hashed_password = user_data[2]  # Assuming the hashed password is the third column (index 2) in the users_signup table.

            # Verify the password using bcrypt
            if bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8')):
                role = user_data[3]  # Assuming the role is the fourth column (index 3) in the users_signup table.

                if role == 'trainer':
                    # Fetch trainer details from the trainers table using contact number
                    db_cursor.execute("SELECT trainer_id, trainer_name, trainer_status FROM trainer WHERE trainer_contact=%s", (contact,))
                    trainer_data = db_cursor.fetchone()

                    if trainer_data:
                        trainer_id, trainer_name, trainer_status = trainer_data

                        session['trainer_name'] = trainer_name  # Store the trainer's name in the session

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
                        session['participant_status'] = participant_data[2]  # Store participant data in the session

                        # Fetch training_location_id based on the participant's training_location_id
                        training_location_id = participant_data[3]  
                        print("Training Location ID:", training_location_id)  # Debugging statement

                        # Fetch training_location_address based on the participant's training_location_id
                        db_cursor.execute("SELECT training_location_address FROM training_locations_list WHERE training_location_id = %s", (training_location_id,))
                        training_location_address = db_cursor.fetchone()
                        print("Training Location Address Query Result:", training_location_address)  # Debugging statement

                        if training_location_address:
                            training_location_address = training_location_address[0]  # Extract the value from the tuple
                            # Store the training location address in the session
                            session['participant_training_location'] = training_location_address
                        else:
                            print("Training Location Address not found in the database")  # Debugging statement

                        # Fetch session data and corresponding trainer data using inner join
                        db_cursor.execute("SELECT s.actual_datetime, s.picture_path, s.video_path, t.trainer_name, t.trainer_contact, tl.training_location_address FROM sessions s INNER JOIN trainer t ON s.trainer_id = t.trainer_id INNER JOIN participants p ON s.participant_id = p.participant_id INNER JOIN training_locations_list tl ON p.training_location_id = tl.training_location_id WHERE s.participant_id = %s", (session['participant_id'],))
                        session_trainer_data = db_cursor.fetchall()
                        # Print the fetched data
                        print("Session Trainer Data:", session_trainer_data)

                        if session_trainer_data:
                            # Store combined session and trainer data in the session
                            session['session_trainer_data'] = session_trainer_data

                            return render_template('participant_display.html', role=role)
                        else:
                            return "Session and Trainer data not found."
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
        return f"An error occurred: {str(e)}"
    finally:
        # Close the cursor and connection here, after you're done using them
        if db_cursor is not None:
            db_cursor.close()

@logins_bp.route('/update_participant_statuses', methods=['POST'])
def update_participant_statuses():
    try:
        participant_data = request.json  # Get participant data as JSON from the request

        db_connection = get_db_connection()
        db_cursor = db_connection.cursor()

        for data in participant_data:
            participant_id = data['participantId']
            new_status = data['participantStatus']

            # Update the participant's status in the database
            db_cursor.execute("UPDATE participants SET participant_status = %s WHERE participant_id = %s", (new_status, participant_id))

        db_connection.commit()
        db_cursor.close()

        return "Participant statuses updated successfully."

    except Exception as e:
         print("An error occurred during database query:", str(e))
    return f"An error occurred: {str(e)}"

@logins_bp.route('/logout', methods=['POST'])
def logout():
    role = session.get('role')
    if role == 'participant':
        # remove the username from the session if it is there
        session.pop('participant_id', None)
        session.pop('participant_name', None)
        session.pop('role', None)
    elif role == 'trainer':
        session.pop('trainer_id', None)
        session.pop('trainer_name', None)
        session.pop('role', None)
    elif role == 'admin':
        session.pop('role', None)
        # Log out an admin when role is None and contact is None
        if role is None and session.get('contact') is None:
            session.clear()  # Clear all session variables
            return "Logged out successfully."

    return redirect(url_for('logins.index'))
