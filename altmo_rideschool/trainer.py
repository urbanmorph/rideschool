print("import feane/ trainer.py")
from flask import Blueprint, render_template, request
##from flask import session, url_for, current_app
#from .db import get_db_connection
from altmo_utils.db import get_db_cursor, get_db_connection


#import psycopg2
##import json
##from .config.config import get_config_value 

trainer_bp = Blueprint('trainer_bp', __name__)



# Configure database connection
##db_host = get_config_value('db_host')
##db_user = get_config_value('db_user')
##db_password = get_config_value('db_password')
##db_name = get_config_value('db_name')

# Function to generate the trainer code
def generate_trainer_code(trainer_id):
    code_prefix = 'PST2023'
    return f"{code_prefix}{trainer_id}"

# Route to the trainer form page
@trainer_bp.route('/trainer-form', methods=['GET'])
def trainer_form():
    try:
        
        with get_db_connection() as connection:
            cursor = connection.cursor()

        # Fetch training locations from the table
            cursor.execute("SELECT organisation_name FROM organisation")
            organisation_names = cursor.fetchall()
            organisation_names = [name[0] for name in organisation_names]

       
        # Render the form template with the training locations
        return render_template('trainer_form.html', organisation_names=organisation_names)
    except Exception as e:
        return f"Error: {str(e)}"

# Route to handle form submission
@trainer_bp.route('/register', methods=['POST'])
def submit_form():
    try:
        # Get the form data
        trainer_name = request.form['trainer_name']
        trainer_email = request.form['trainer_email']
        trainer_contact = request.form['trainer_contact']
        trainer_address = request.form['trainer_address']
        trainer_age = request.form['trainer_age']
        trainer_gender = request.form['trainer_gender']
        trainer_education = request.form['trainer_education']
        trainer_languages = request.form.getlist('trainer_language')
        trainer_aadhar_no = request.form['trainer_aadhar_no']
        organisation_name = request.form['organisation_name']

        # Connect to the database
        ##connection = psycopg2.connect(
          ##  host=db_host,
            ##user=db_user,
            ##password=db_password,
            ##dbname=db_name
        ##)
        with get_db_connection() as connection:
            cursor = connection.cursor()

        # Fetch the organisation_id based on the selected organisation_name
            select_query = "SELECT organisation_id FROM organisation WHERE organisation_name = %s"
            cursor.execute(select_query, (organisation_name,))
            organisation_id = cursor.fetchone()[0]
    
       #Note :  admin sets the traing_location

       # Insert trainer data into the trainers table
            insert_query = '''
            INSERT INTO trainer (trainer_name, trainer_email, trainer_contact, trainer_address, trainer_age, trainer_gender, trainer_education, trainer_language, trainer_aadhar_no, organisation_id, training_location_id, trainer_training_completion_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, '0001-01-01')
            RETURNING trainer_id
            '''

            values = (trainer_name, trainer_email, trainer_contact, trainer_address, trainer_age, trainer_gender, trainer_education, trainer_languages, trainer_aadhar_no, organisation_id, 0)
            cursor.execute(insert_query, values)
            new_trainer_id = cursor.fetchone()[0]

        # Generate the code for the trainer
            new_code = generate_trainer_code(new_trainer_id)

        # Update the code with the generated code
            update_query = "UPDATE trainer SET trainer_code = %s WHERE trainer_id = %s;"
            cursor.execute(update_query, (new_code, new_trainer_id))

        # Commit the transaction
            connection.commit()

        # Close the cursor and connection
        #cursor.close()
        #connection.close()

        # Redirect to a success page or any other desired page
        return "Trainer registered successfully!"
    except Exception as e:
        return f"Error: {str(e)}"






