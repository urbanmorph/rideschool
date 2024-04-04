print("signup.py")

import bcrypt
import traceback
import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from altmo_utils.db import get_db_cursor

signup_bp = Blueprint('signup', __name__)

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
            with get_db_cursor() as db_cursor:
                db_cursor.execute("SELECT * FROM users_signup WHERE contact_no=%s", (contact,))
                existing_user = db_cursor.fetchone()

            if existing_user:
                return jsonify(alert_type='danger', message=f"An account with the provided contact number {contact} already exists. Kindly proceed to login.")

            # Check if the contact is in the participants table
            with get_db_cursor() as db_cursor:
                db_cursor.execute("SELECT * FROM participants WHERE contact=%s", (contact,))
                existing_participant = db_cursor.fetchone()

            if existing_participant:
                role = "participant"
                user_password = form.password.data
                confirm_password = form.confirm_password.data

                # Perform password validation (implement any additional complexity requirements here)
                if user_password != confirm_password:
                    return jsonify(alert_type='danger', message="Passwords do not match. Please try again.")

                # Store the data in the users_signup table
                hashed_password = hash_password(user_password)
                with get_db_cursor(commit=True) as db_cursor:
                    db_cursor.execute("INSERT INTO users_signup (contact_no, password, role) VALUES (%s, %s, %s)", (contact, hashed_password, role))
                #return jsonify(alert_type='success', message="Your account has been created successfully.")
                return jsonify(alert_type='success', message=f"Hello {role.capitalize()}, Your account has been created successfully.")

            # Check if the contact is in the trainer table
            with get_db_cursor() as db_cursor:
                db_cursor.execute("SELECT * FROM trainer WHERE contact=%s", (contact,))
                trainer = db_cursor.fetchone()

                # Determine the role based on whether the contact exists in trainer or participants table
                if existing_participant:
                    role = "participant"

                elif trainer:
                    role = "trainer"
                    # Check if the trainer_status is CERTIFIED
                    with get_db_cursor() as db_cursor:
                        db_cursor.execute("SELECT status FROM trainer WHERE contact=%s", (contact,))
                        trainer_status_record = db_cursor.fetchone()

                    # Check if trainer_status_record is not None and 'trainer_status' is present in the record
                    if trainer_status_record and 'status' in trainer_status_record:
                        trainer_status = trainer_status_record['status']

                        if trainer_status == "CERTIFIED":
                            user_password = form.password.data
                            confirm_password = form.confirm_password.data

                            # Perform password validation (implement any additional complexity requirements here)
                            if user_password != confirm_password:
                                return jsonify(alert_type='danger', message="Password and Confirm Password do not match. Please try again.")

                            # Store the data in the users_signup table
                            hashed_password = hash_password(user_password)
                            with get_db_cursor(commit=True) as db_cursor:
                                db_cursor.execute("INSERT INTO users_signup (contact_no, password, role) VALUES (%s, %s, %s)", (contact, hashed_password, role))

                            return jsonify(alert_type='success', message=f"Hello {role.capitalize()}, you have created an account successfully.")

                        else:
                            return jsonify(alert_type='danger', message="Admin approval is required to proceed with your account creation. Please await confirmation from the admin.")
                else:
                    return jsonify(alert_type='danger', message=f"The contact number {contact} is not registered as a participant or a trainer.")
        
        else:
                errors = {field.name: field.errors[0] if field.errors else None for field in form}
                return jsonify(alert_type='danger', errors=errors)

    except Exception as e:
        print("An error occurred while processing the signup:")
        traceback.print_exc()
        error_message = f"An error occurred while processing the signup.{str(e)}"
        return jsonify(alert_type='danger', message=error_message)


def hash_password(password):
    # Generate a random salt using bcrypt
    
    salt = bcrypt.gensalt()

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')
