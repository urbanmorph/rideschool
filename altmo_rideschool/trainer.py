print("trainer.py")
from flask import Blueprint, render_template, request, jsonify
from altmo_utils.db import get_db_cursor 
import traceback 
trainer_bp = Blueprint('trainer_bp', __name__)

# Function to generate the trainer code
def generate_trainer_code(trainer_id):
    code_prefix = 'PST2023'
    return f"{code_prefix}{trainer_id}"

# Route to the trainer form page
@trainer_bp.route('/trainer-form', methods=['GET'])
def trainer_form():
    try:        
        with get_db_cursor(commit=False) as cursor:
            # Fetch training locations from the table
            cursor.execute("SELECT name FROM organisation")
            # Fetch the 'organisation_name' column from each row
            rows = cursor.fetchall()
            print("Rows from the database:", rows) 
            organisation_names = [row['name'] for row in rows]
        # Render the form template with the training locations
        return render_template('trainer_form.html', organisation_names=organisation_names)
    except Exception as e:        
        traceback.print_exc()  # Print the full traceback to the console
        return "An error occurred. Please check the console for details."
# Route to handle form submission
@trainer_bp.route('/register', methods=['POST'])
def submit_form():
    try:
        name = request.form['name']
        trainer_email = request.form['trainer_email']
        trainer_contact = request.form['trainer_contact']
        trainer_address = request.form['trainer_address']
        trainer_age = request.form['trainer_age']
        trainer_gender = request.form['trainer_gender']
        trainer_education = request.form['trainer_education']
        trainer_languages = request.form.getlist('trainer_language')
        trainer_aadhar_no = request.form['trainer_aadhar_no']
        organisation_name = request.form['organisation_name']
        
        with get_db_cursor(commit=True) as cursor:        
            check_query = "SELECT id FROM trainer WHERE contact = %s"
            cursor.execute(check_query, (trainer_contact,))
            existing_trainer = cursor.fetchone()

            if existing_trainer:                              
                return jsonify({"alert_type": "error", "message": "The contact number is currently registered. Please await certification before proceeding with the account creation."})

            # Fetch the organisation_id based on the selected organisation_name
            select_query = "SELECT id FROM organisation WHERE name = %s"
            cursor.execute(select_query, (organisation_name,))
            #organisation_id = cursor.fetchone()[0]
            result = cursor.fetchone()
            
            if result and 'id' in result:
                organisation_id = result['id']
            else:
                # Handle the case where organisation_id is not found
                return jsonify({"alert_type": "error", "message": "Organisation not found."})
    
            #Note :  admin sets the traing_location
            # Insert trainer data into the trainers table
            insert_query = '''
            INSERT INTO trainer (name, email, contact, address, age, gender, education, language, aadhar_no, org_id, t_location_id, training_completion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, '0001-01-01')
            RETURNING id
            '''
            values = (name, trainer_email, trainer_contact, trainer_address, trainer_age, trainer_gender, trainer_education, trainer_languages, trainer_aadhar_no, organisation_id, 0)
            cursor.execute(insert_query, values)
            new_trainer_id = cursor.fetchone()
            # Extract the trainer_id from the dictionary
            if new_trainer_id and 'id' in new_trainer_id:
                new_trainer_id = new_trainer_id['id']
            else:
                # Handle the case where trainer_id is not found                                
                return jsonify({"alert_type": "error", "message": "Trainer ID not found."})
            
            # Generate the code for the trainer
            new_code = generate_trainer_code(new_trainer_id)

            # Update the code with the generated code
            update_query = "UPDATE trainer SET code = %s WHERE id = %s;"
            cursor.execute(update_query, (new_code, new_trainer_id))

        # Redirect to a success page or any other desired page
        return jsonify({"alert_type": "success", "message": "Registration successful!"})
      
    except Exception as e:       
        traceback.print_exc()
        return jsonify({"alert_type": "error", "message": "An error occurred. Please try again later "})
      
    
