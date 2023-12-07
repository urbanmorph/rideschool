# organization.py

print("import feane/ organization.py")
import traceback
from flask import Blueprint, render_template, request, current_app, send_from_directory, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
#from .db import get_db_cursor
from altmo_utils.db import get_db_cursor

organization_bp = Blueprint('organization', __name__)

@organization_bp.route('/organization-form')
def organization_form():
    return render_template('organization_form.html')

@organization_bp.route('/submit_organization', methods=['POST'])
def submit_organization():
    try:
        # Retrieve form data
        organization_name = request.form['organization-name']
        organization_address = request.form['organization-address']
        organization_contact = request.form['organization-contact']
        organization_email = request.form['organization-email']
        organization_type = request.form['organization-type']
        organization_activities = request.form['organization-activities']
        coordinator_name = request.form['coordinator-name']
        coordinator_email = request.form['coordinator-email']
        coordinator_contact = request.form['coordinator-contact']

        # Handle file upload
        #legal_status_document = request.files['organization-legal-status-document']
        #file_path = None

        #if legal_status_document:
            # Generate a unique filename using UUID and save to the upload folder
         #   filename = str(uuid.uuid4()) + secure_filename(legal_status_document.filename)
          #  file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename)
           # legal_status_document.save(file_path)
        #if legal_status_document:
            # Ensure the directory exists
            #if not os.path.exists(current_app.config['ORGANIZATION_FOLDER']):
               # os.makedirs(current_app.config['ORGANIZATION_FOLDER'])

            # Generate a unique filename using UUID and save to the upload folder
            #filename = str(uuid.uuid4()) + secure_filename(legal_status_document.filename)
            #file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename)
            ##file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename.replace('/', '\\'))
            # Print the generated file path for debugging
           # file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename)
            #file_path = file_path.replace('/', os.path.sep)
           ## print("Generated file path:", file_path)

            #legal_status_document.save(file_path)
        
        organization_legal_status_document = request.files['organization-legal-status-document']
        if organization_legal_status_document:
            document_filename = secure_filename(organization_legal_status_document.filename)
            relative_document_path = os.path.join('static', 'organization_image', document_filename)
            document_path_full = os.path.join(current_app.root_path, current_app.config['ORGANIZATION_FOLDER'], document_filename)

    # Ensure the directory exists
            os.makedirs(os.path.dirname(document_path_full), exist_ok=True)

    # Save the document
            organization_legal_status_document.save(document_path_full)


        # Perform database insertion or any other necessary operations
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                INSERT INTO public.organisation (
                    organisation_name, 
                    organisation_address, 
                    organisation_contact, 
                    organisation_email, 
                    organisation_type, 
                    organisation_activities, 
                    organisation_legal_status_document, 
                    coordinator_name, 
                    coordinator_email,
                    coordinator_contact
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            """, (
                organization_name,
                organization_address,
                organization_contact,
                organization_email,
                organization_type,
                organization_activities,
                relative_document_path, 
                coordinator_name,
                coordinator_email,
                coordinator_contact
            ))

        # Display success message
        message = f"Organization {organization_name} submitted successfully!"
        return jsonify({'status': 'success', 'message': message})

    except Exception as e:
        traceback.print_exc()
        # Log the exception for debugging purposes
        print(f"An error occurred: {e}")

        # Display error message
        return jsonify({'status': 'error', 'message': 'An error occurred. Please try again.'})


#@organization_bp.route('/organization_image/<filename>')
#def display_image(filename):
 #   return send_from_directory(current_app.config['ORGANIZATION_FOLDER'], filename)

##"D:\job\urban_morph\pedal_shaale_project\altmo_rideschool\static\organization_image"
#@organization_bp.route('/display_legal_document/<filename>')
#def display_legal_document(filename):
   
 #   return send_from_directory(current_app.config['ORGANIZATION_FOLDER'], filename)
@organization_bp.route('/display_legal_document/<filename>')
def display_legal_document(filename):
    return send_from_directory(current_app.config['ORGANIZATION_FOLDER'], filename)