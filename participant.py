from flask import Blueprint, render_template, request, session
import psycopg2
from datetime import datetime

participant_bp = Blueprint('participant_bp', __name__)

# Configure database connection
db_host = '127.0.0.1'
db_user = 'postgres'
db_password = 'root'
db_name = 'Pedal_Shaale'

# Function to generate the participant code
def generate_participant_code(participant_id):
    code_prefix = 'PSP2023'
    return f"{code_prefix}{participant_id}"

# Route to the participant form page
@participant_bp.route('/participant-form', methods=['GET'])
def participant_form():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch training locations from the table
        cursor.execute("SELECT training_location, training_location_address FROM training_locations_list")
        training_locations = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

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
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch the training_location_id based on the selected training_location
        select_query = "SELECT training_location_id FROM training_locations_list WHERE training_location = %s"
        cursor.execute(select_query, (training_location,))
        training_location_id = cursor.fetchone()[0]

        # Insert participant data into the participants table with participant_created_date and participant_updated_date
        insert_query = "INSERT INTO participants (participant_name, participant_email, participant_contact, participant_address, participant_age, participant_gender, training_location_id, participant_status, participant_created_date, participant_updated_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING participant_id"
        values = (participant_name, participant_email, participant_contact, participant_address, participant_age, participant_gender, training_location_id, participant_status, participant_created_date, participant_updated_date)
        cursor.execute(insert_query, values)

        # Fetch the newly inserted participant_id
        new_participant_id = cursor.fetchone()[0]

        # Generate the code for the participant using the fetched participant_id
        new_code = generate_participant_code(new_participant_id)

        # Update the participant's code in the database
        update_query = "UPDATE participants SET participant_code = %s WHERE participant_id = %s"
        cursor.execute(update_query, (new_code, new_participant_id))

        # Commit the transaction
        connection.commit()
        cursor.close()
        connection.close()

        # Return the success message
        return "Participant registered successfully!!!"
    except Exception as e:
        # Print statement to print the error for debugging
        print(f"Error: {str(e)}")

        # Return an error message
        return f"Error: {str(e)}"


# Route to view the participant form table

# i am not using this rout anymore (check once)
@participant_bp.route('/participant-table', methods=['GET'])
def participant_table():
    try:
        print(" trying to access  the datacase ")
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch participant data from the table
        cursor.execute("SELECT * FROM participants")
        participant_data = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Render the participant form table template with the participant data
        return render_template('participant_form_table.html', participant_data=participant_data)
    except Exception as e:
        
        return f"Error: {str(e)}"
     

#end rout 

@participant_bp.route('/participant_session_info', methods=['GET'])
def participant_session_info():
    try:
        # Check if a participant is logged in
        if session.get('role') == 'participant':
            participant_id = session.get('participant_id')

            # Add a print statement for debugging
            print("Attempting to connect to the database...")

            # Connect to the database
            connection = psycopg2.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                dbname=db_name
            )

            print("Connected to the database.")  # Add another print statement

            cursor = connection.cursor()

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

            # Close the database connection
            cursor.close()
            connection.close()

            # Render the template with session details
            return render_template('participant_session_info.html', session_details=session_details)
        else:
            return "You must be logged in as a participant to view session details."
    except Exception as e:
        print(f"Error: {str(e)}")  # Print the error for debugging
        return f"Error: {str(e)}"
    
    # Route to display trainer information for all trainers
@participant_bp.route('/participant-info', methods=['GET'])
def participant_info():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch trainer details for all participants
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

        # Render the trainer_info.html template with the list of trainers
        return render_template('participant_info.html', participants=participants)
    except Exception as e:
        return f"Error: {str(e)}"
