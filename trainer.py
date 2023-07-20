from flask import Blueprint, render_template, request
import psycopg2

# Create a Blueprint for the trainer module
trainer_bp = Blueprint('trainer', __name__)

# Configure database connection
db_host = 'localhost'
db_user = 'postgres'
db_password = 'root'
db_name = 'Pedal_Shaale'

# Route to the trainer form page
@trainer_bp.route('/trainer-form', methods=['GET'])
def trainer_form():
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
        cursor.execute("SELECT organisation_name FROM organisation")
        organisation_names = cursor.fetchall()
        organisation_names = [name[0] for name in organisation_names]

        # Close the database connection
        cursor.close()
        connection.close()

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
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch the organisation_id based on the selected organisation_name
        select_query = "SELECT organisation_id FROM organisation WHERE organisation_name = %s"
        cursor.execute(select_query, (organisation_name,))
        organisation_id = cursor.fetchone()[0]

        # Insert trainer data into the trainers table
        insert_query = '''
        INSERT INTO trainer (trainer_name, trainer_email, trainer_contact, trainer_address, trainer_age, trainer_gender, trainer_education, trainer_language, trainer_aadhar_no, organisation_id, trainer_training_completion_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '0001-01-01')
        '''
        values = (trainer_name, trainer_email, trainer_contact, trainer_address, trainer_age, trainer_gender, trainer_education, trainer_languages, trainer_aadhar_no, organisation_id)
        cursor.execute(insert_query, values)

        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Redirect to a success page or any other desired page
        return "Trainer registered successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

# Route to display the trainer table
@trainer_bp.route('/trainer-table', methods=['GET'])
def trainer_table():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()

        # Fetch trainers from the table
        cursor.execute("SELECT * FROM trainer")
        trainers = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Render the trainer table template
        return render_template('trainer_table.html', trainers=trainers)
    except Exception as e:
        return f"Error: {str(e)}"
