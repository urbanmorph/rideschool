from flask import Blueprint, render_template, request
import psycopg2
from datetime import datetime

participant_bp = Blueprint('participant', __name__)

# Configure database connection
db_host = 'localhost'
db_user = 'postgres'
db_password = 'root'
db_name = 'Pedal_Shaale'

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
        insert_query = "INSERT INTO participants (participant_name, participant_email, participant_contact, participant_address, participant_age, participant_gender, training_location_id, participant_status, participant_created_date, participant_updated_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (participant_name, participant_email, participant_contact, participant_address, participant_age, participant_gender, training_location_id, participant_status, participant_created_date, participant_updated_date)
        cursor.execute(insert_query, values)

        # Commit the transaction
        connection.commit()

        # Fetch the training_location_address based on the training_location_id
        select_location_address_query = "SELECT training_location_address FROM training_locations_list WHERE training_location_id = %s"
        cursor.execute(select_location_address_query, (training_location_id,))
        training_location_address_result = cursor.fetchone()

        if training_location_address_result is not None:
            training_location_address = training_location_address_result[0]
        else:
            training_location_address = "N/A"

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Construct the success message with additional details
        success_message = "Participant registered successfully!<br><br>"
        success_message += "Additional Details:<br>"
        success_message += f"Training Location Address: {training_location_address}<br><br>"

        # Return the success message
        return success_message
    except Exception as e:
        return f"Error: {str(e)}"

# Route to view the participant form table
@participant_bp.route('/participant-table', methods=['GET'])
def participant_table():
    try:
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
