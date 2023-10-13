import bcrypt
import psycopg2
import os
import logging
from base64 import urlsafe_b64encode
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

# Import the necessary libraries for form validation
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from config.config import get_config_value 

signup_bp = Blueprint('signup', __name__)
#create a store it in a
#  config file , pool
# PostgreSQL database connection
db_connection = psycopg2.connect(
    host=get_config_value('db_host'),
    database=get_config_value('db_name'),
    user=get_config_value('db_user'),
    password=get_config_value('db_password')
)
db_cursor = db_connection.cursor()

# Define a form for the signup page
class SignupForm(FlaskForm):
    contact = StringField('Contact Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Signup')

@signup_bp.route('/signup')
def index():
    form = SignupForm()
    return render_template('signup.html', form=form)



@signup_bp.route('/check_contact', methods=['POST'])
def check_contact():
    try:
        form = SignupForm(request.form)
        logging.info("Entering check_contact function")
        if form.validate():
            contact = form.contact.data

            # Check if the contact is already registered in the users_signup table
            db_cursor.execute("SELECT * FROM users_signup WHERE contact_no=%s", (contact,))
            existing_user = db_cursor.fetchone()

            if existing_user:
                return jsonify(alert_type='danger', message=f"The contact number {contact} is already registered.")

            # Check if the contact is in the participants table
            db_cursor.execute("SELECT * FROM participants WHERE participant_contact=%s", (contact,))
            existing_participant = db_cursor.fetchone()

            if existing_participant:
                role = "participant"
                user_password = form.password.data
                confirm_password = form.confirm_password.data

                # Perform password validation (implement any additional complexity requirements here)
                if user_password != confirm_password:
                    return jsonify(alert_type='danger', message="Password and Confirm Password do not match. Please try again.")

                # Store the data in the users_signup table
                hashed_password = hash_password(user_password)
                db_cursor.execute("INSERT INTO users_signup (contact_no, password, role) VALUES (%s, %s, %s)", (contact, hashed_password, role))
                db_connection.commit()

                return jsonify(alert_type='success', message=f"Hello {role.capitalize()}, you have created an account successfully!")

            

            # Check if the contact is in the trainer table
            db_cursor.execute("SELECT * FROM trainer WHERE trainer_contact=%s", (contact,))
            trainer = db_cursor.fetchone()

            # Determine the role based on whether the contact exists in trainer or participants table
            if existing_participant:
               role = "participant"

            elif trainer:
                role = "trainer"
                # Check if the trainer_status is CERTIFIED
                db_cursor.execute("SELECT trainer_status FROM trainer WHERE trainer_contact=%s", (contact,))
                trainer_status = db_cursor.fetchone()

                if trainer_status and trainer_status[0] == "CERTIFIED":
                    user_password = form.password.data
                    confirm_password = form.confirm_password.data

                    # Perform password validation (implement any additional complexity requirements here)
                    if user_password != confirm_password:
                        return jsonify(alert_type='danger', message="Password and Confirm Password do not match. Please try again.")

                    # Store the data in the users_signup table
                    hashed_password = hash_password(user_password)
                    db_cursor.execute("INSERT INTO users_signup (contact_no, password, role) VALUES (%s, %s, %s)", (contact, hashed_password, role))
                    db_connection.commit()

                    return jsonify(alert_type='success', message=f"Hello {role.capitalize()}, you have created an account successfully!")

                else:
                    return jsonify(alert_type='danger', message="You are not CERTIFIED. You can create an account after you are certified as a Trainer.")
            else:
                return jsonify(alert_type='danger', message=f"The contact number {contact} is not registered as a participant or a trainer.")
        
        else:
            errors = {field.name: field.errors[0] if field.errors else None for field in form}
            return jsonify(alert_type='danger', errors=errors)

    except psycopg2.IntegrityError as e:
        db_connection.rollback()
        logging.exception("An IntegrityError occurred while processing the signup:")
        error_message = "An error occurred while processing the signup."
        return jsonify(alert_type='danger', message=error_message)

    except Exception as e:
        db_connection.rollback()
        logging.exception("An error occurred while processing the signup:")
        error_message = "An error occurred while processing the signup."
        return jsonify(alert_type='danger', message=error_message)



def hash_password(password):
    # Generate a random salt using bcrypt
    salt = bcrypt.gensalt()

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')
