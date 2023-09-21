# Import required modules at the top of your Flask application
import bcrypt
import psycopg2
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify 
from flask import current_app
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
        updates = request.get_json()  # ( requesting to get what ever data is present inside the updates arra in the json format )Parse JSON data from the request , updates = request.get_json(): This line retrieves the JSON data from the POST request sent by the client. It expects the client to send an array of updates.

        # Initialize db_cursor
        db_cursor = get_db_connection().cursor()

        # Iterate through the received updates and update the database, For each update, it extracts the participant ID and the new status. It also validates that the participant ID is a valid intege
        for update in updates:
            participant_id = update.get('participantId')
            new_status = update.get('newStatus')

            # Validate that participant_id is a valid integer
            try:
                participant_id = int(participant_id)
            except ValueError:
                return f"Invalid participant ID: {update.get('participantId')}"

            # Perform database update using the retrieved data
            db_cursor.execute("UPDATE participants SET participant_status = %s WHERE participant_id = %s", (new_status, participant_id))

        # Commit the changes to the database
        db_connection.commit()

        #If any errors occur during this process, it logs the error and rolls back the changes to maintain data consistency.

        return jsonify({"success": True, "participantId": participant_id, "newStatus": new_status})

    except Exception as e:
        # Log the error
        current_app.logger.error("An error occurred during database update: %s", str(e))

        # Rollback changes if any error occurs
        db_connection.rollback()

        return jsonify({"success": False, "error": "An error occurred. Please check the logs for more information."})
    finally:

        # Close the cursor and connection here, after you're done using them
        if db_cursor is not None:
            db_cursor.close()


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

@logins_bp.route('/trainer_details')
def trainer_details():
    role = session.get('role')
    if role != 'trainer':
        return redirect(url_for('logins.index'))  # Redirect to the login page if not a trainer

    try:
        db_connection = get_db_connection()  # Get or create a database connection
        db_cursor = db_connection.cursor()

        trainer_id = session.get('trainer_id')  # Get trainer_id from session

        # Fetch trainer details
        db_cursor.execute("SELECT trainer_name, trainer_status FROM trainer WHERE trainer_id = %s", (trainer_id,))
        trainer_data = db_cursor.fetchone()

        if trainer_data:
            trainer_name, trainer_status = trainer_data

            # Fetch participant data based on the trainer's training location
            db_cursor.execute("SELECT participant_id, participant_name, participant_contact, participant_status FROM participants WHERE training_location_id = (SELECT training_location_id FROM trainer WHERE trainer_id = %s) AND (participant_status = 'ONGOING' OR participant_status = 'NEW')", (trainer_id,))
            participant_data = db_cursor.fetchall()

            # populating  the dropdown list from the database that is from the constraints that i have set that only i am making as options , Fetch valid status values from the database constraint
            db_cursor.execute("SELECT unnest(enum_range(NULL::participant_status))")
            valid_status_values = [status[0] for status in db_cursor.fetchall()]

            return render_template('trainer_details.html', role=role, trainer_name=trainer_name, participants=participant_data, valid_status_values=valid_status_values)
        else:
            return "Trainer details not found."

    except Exception as e:
        print("An error occurred during trainer details retrieval:", str(e))
        return f"An error occurred: {str(e)}"
    finally:
        # Close the cursor and connection here, after you're done using them
        if db_cursor is not None:
            db_cursor.close()
