print("import feane/ participant.py")
from flask import Blueprint, render_template, request, session , redirect, url_for, jsonify
##import psycopg2
from datetime import datetime
#from .config.config import get_config_value  
#from altmo_utils.db  import get_db_pool  # Import the get_db_pool function
from altmo_utils.db import get_db_cursor
import traceback

participant_bp = Blueprint('participant_bp', __name__)

# Retrieve database connection parameters from the configuration
# Configure database connection
##db_host = get_config_value('db_host')
##db_user = get_config_value('db_user')
##db_password = get_config_value('db_password')
##db_name = get_config_value('db_name')

# Function to generate the participant code
def generate_participant_code(participant_id):
    code_prefix = 'PSP2023'
    return f"{code_prefix}{participant_id}"


# Route to the participant form page
@participant_bp.route('/participant-form', methods=['GET'])
def participant_form():
    try:
        # Use a cursor from the pool
        with get_db_cursor(commit=False) as cursor:
            # Fetch training locations from the table
            cursor.execute("SELECT training_location, training_location_address FROM training_locations_list")
            training_locations = cursor.fetchall()

            print("Query executed successfully.")

        # Render the form template with the training locations
        return render_template('participant_form.html', training_locations=training_locations)
    except Exception as e:
        return f"Error: {str(e)}"

# Route to handle form submission

@participant_bp.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Get the form data
        participant_name = request.form['participant_name']
        participant_email = request.form['participant_email']
        participant_contact = request.form['participant_contact']
        participant_address = request.form['participant_address']
        participant_age = request.form['participant_age']
        participant_gender = request.form['participant_gender']
        training_location = request.form['training_location']
        participant_status = "NEW"
        participant_created_date = datetime.now()
        participant_updated_date = participant_created_date  # Update participant_updated_date to participant_created_date initially

        # Connect to the database
        with get_db_cursor(commit=True) as cursor: 
            # Check if the contact number already exists
            check_contact_query = "SELECT participant_id FROM participants WHERE participant_contact = %s"
            cursor.execute(check_contact_query, (participant_contact,))
            existing_participant = cursor.fetchone()

            if existing_participant:
                # Display a message if the contact number is already registered
               # return jsonify({"message": "Contact number is already registered. Continue to create an account.", "type": "info"})
                return "Contact number is already registered. Continue to create an account!!!"

          
            else:# Fetch the training_location_id based on the selected training_location
                select_query = "SELECT training_location_id FROM training_locations_list WHERE training_location = %s"
                cursor.execute(select_query, (training_location,))
                result = cursor.fetchone()

                if result is not None and 'training_location_id' in result:
                # Use the key 'training_location_id' to access the value
                    training_location_id = result['training_location_id']
                else:
                # Handle the case when fetchone() returns None (no matching record found)
                   # error_message = "Training location not found or missing 'training_location_id' in the result."
                    #print(error_message)
                    #return error_message
                    return "Training location not found or missing 'training_location_id' in the result."


        # Insert participant data into the participants table with participant_created_date and participant_updated_date
                insert_query = "INSERT INTO participants (participant_name, participant_email, participant_contact, participant_address, participant_age, participant_gender, training_location_id, participant_status, participant_created_date, participant_updated_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING participant_id"
                values = (participant_name, participant_email, participant_contact, participant_address, participant_age, participant_gender, training_location_id, participant_status, participant_created_date, participant_updated_date)
                cursor.execute(insert_query, values)

        # Fetch the newly inserted participant_id
            #new_participant_id = cursor.fetchone()
                new_participant_row = cursor.fetchone()

                if new_participant_row:
                # Extract participant_id from the RealDictRow
                    new_participant_id = new_participant_row['participant_id']
            

        # Generate the code for the participant using the fetched participant_id
                    new_code = generate_participant_code(new_participant_id)

        # Update the participant's code in the database
                    update_query = "UPDATE participants SET participant_code = %s WHERE participant_id = %s"
                    cursor.execute(update_query, (new_code, new_participant_id))
                else:
                    error_message = "Error retrieving newly inserted participant_id or result is empty."
                    print(error_message)
                    return error_message
                

        # Return the success message
                #return jsonify({"message": "Participant registered successfully!!!", "type": "success"})
                return "Participant registered successfully!!!"
    except Exception as e:
        # Print statement to print the error for debugging
        print(f"Error: {str(e)}")
        traceback.print_exc()
        # Return an error message
        return f"Error: {str(e)}"
        #return jsonify({"message": f"Error: {str(e)}", "type": "error"})

# Route to view the participant form table

 ##not using open

# i am not using this rout anymore (check once)
@participant_bp.route('/participant-table', methods=['GET'])
def participant_table():
    try:
        print(" trying to access  the datacase ")
        # Connect to the database
        ##connection = psycopg2.connect(
          ##  host=db_host,
            ##user=db_user,
            ##password=db_password,
            ##dbname=db_name
        ##)
        ##cursor = connection.cursor()
        # Get the database connection pool
        with get_db_cursor() as cursor:
        #db_pool = get_db_pool()
         # Use a connection from the pool
        #with db_pool.getconn() as connection:
         #   with connection.cursor() as cursor:

        # Fetch participant data from the table
            cursor.execute("SELECT * FROM participants")
            participant_data = cursor.fetchall()

        # Close the database connection
        #cursor.close()
        #connection.close()

        # Render the participant form table template with the participant data
        return render_template('participant_form_table.html', participant_data=participant_data)
    except Exception as e:
        
        return f"Error: {str(e)}"
    

    
@participant_bp.route('/participant_session_info', methods=['GET'])
def participant_session_info():
    try:
        # Check if a participant is logged in
        if session.get('role') == 'participant':
            participant_id = session.get('participant_id')

            # print statement for debugging
            print("Attempting to connect to the database...")

            # Connect to the database
            with get_db_cursor() as cursor:
            #db_pool = get_db_pool()
            #with db_pool.getconn() as connection:
             #   with connection.cursor() as cursor:
                    # Fetch session details for the logged-in participant
                    cursor.execute("""
                        SELECT
                            s.actual_datetime,
                            s.hours_trained,
                            s.picture_path,
                            s.video_path,
                            s.description,
                            t.trainer_name
                        FROM sessions s
                        JOIN trainer t ON s.trainer_id = t.trainer_id
                        WHERE s.participant_id = %s;
                    """, (participant_id,))
                    session_details = cursor.fetchall()
                    print("Session Details:", session_details)

            # Render the template with session details
            return render_template('participant_session_info.html', session_details=session_details)
        else:
            return "You need to be logged in as a participant to view session details."
    except Exception as e:
        
        print(f"Error: {str(e)}")  # Print the error for debugging
        traceback.print_exc()
        return f"Error: {str(e)}"
 ##not using for now close 

# Route to display the feedback form and handle form submission
@participant_bp.route('/feedback-form', methods=['GET', 'POST'])
def feedback_form():
    try:
        # Check if a participant is logged in
        if session.get('role') == 'participant':
            participant_id = session.get('participant_id')

            # Connect to the database using get_db_cursor
            with get_db_cursor(commit=True) as cursor:

                # Fetch participant details for the logged-in participant
                cursor.execute("SELECT * FROM participants WHERE participant_id = %s", (participant_id,))
                participant = cursor.fetchone()

                if not participant:
                    return "Participant not found."

                print("Participant Status:", participant.get('participant_status'))  # Debug statement

                if request.method == 'POST':
                    # This block handles the form submission (POST request)
                    rate_training_sessions = request.form['training_rating']
                    learner_guide_useful = request.form.get('learner_guide', 'No')
                    feedback = request.form['additional_feedback']
                    confident_to_ride = request.form.get('confidence', 'No')
                    trainer_evaluation = request.form.get('trainer_evaluation', '1')  # Default to 1 if not provided
                    trainer_feedback = request.form['trainer_feedback']

                    # Insert the feedback data into the "feedback" table
                    insert_query = """
                        INSERT INTO feedback (participant_id, rate_training_sessions, learner_guide_useful, feedback, confident_to_ride, trainer_evaluation, trainer_feedback)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (
                        participant_id, rate_training_sessions, learner_guide_useful, feedback, confident_to_ride,
                        trainer_evaluation, trainer_feedback
                    )
                    cursor.execute(insert_query, values)

                    # Commit the transaction
                    # No need to commit explicitly when using get_db_cursor with commit=True

                    # Return a success message
                    response = {"status": "success", "message": "Feedback submitted successfully!"}
                    return jsonify(response)

                elif request.method == 'GET':
                    print("Participant Status:", participant.get('participant_status'))

                    # This block handles the initial form display (GET request)
                    if participant.get('participant_status') == 'COMPLETED':
                        sql_query = """
                            SELECT
                                p.participant_name,
                                p.participant_code,
                                p.participant_updated_at,
                                COUNT(s.hours_trained) AS session_count,  -- Calculate the count of sessions
                                t.trainer_name
                            FROM
                                participants p
                            JOIN
                                sessions s ON p.participant_id = s.participant_id
                            JOIN
                                trainer t ON s.trainer_id = t.trainer_id
                            WHERE
                                p.participant_status = 'COMPLETED'
                            AND
                                p.participant_id = %s
                            GROUP BY
                                p.participant_name, p.participant_code, p.participant_updated_at, t.trainer_name
                        """

                        cursor.execute(sql_query, (participant_id,))
                        result = cursor.fetchone()
                        print("SQL Query Result:", result)

                        return render_template('feedback.html', participant=participant, result=result)

                    else:
                        return "You must be logged in as a participant with 'COMPLETED' status to access the feedback form."
                else:
                    return "Participant not found."
        else:
            return "You must be logged in as a participant to access the feedback form."
    except Exception as e:
        traceback.print_exc()
        response = {"status": "error", "message": "An error occurred."}
        return jsonify(response)