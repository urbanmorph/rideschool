# organization.py
print("organization.py")
import traceback
from flask import Blueprint, render_template, request, current_app, send_from_directory, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
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
        organization_legal_status_document = request.files['organization-legal-status-document']
        if organization_legal_status_document:            
            document_filename = secure_filename(organization_legal_status_document.filename)        
            relative_document_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], document_filename) #current_app.config['ORGANIZATION_FOLDER']: "This retrieves the value" of 'ORGANIZATION_FOLDER' from your Flask app's configuration.            
            document_path_full = os.path.join(current_app.root_path, relative_document_path)
            # Ensure the directory exists
            print("relative_document_path:",relative_document_path)
            print("document_path_full:",document_path_full)
            os.makedirs(os.path.dirname(document_path_full), exist_ok=True)

            # Save the document
            organization_legal_status_document.save(document_path_full)

            # Perform database insertion or any other necessary operations
            with get_db_cursor(commit=True) as cursor:
                # check if contact no is already registered 
                chech_contact = "SELECT id FROM organisation WHERE contact = %s"
                cursor.execute(chech_contact, (organization_contact,))
                existing_org = cursor.fetchone()
                    
                if existing_org:
                    return jsonify({"alert_type ": "error", "message": "Organization with this contact number is already registered."})

                cursor.execute("""
                INSERT INTO public.organisation (
                    name, 
                    address, 
                    contact, 
                    email, 
                    org_type, 
                    activities, 
                    legal_document, 
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
        message = f"{organization_name} has been registered successfully!"
        return jsonify({'alert_type ': 'success', 'message': message})
      
    except Exception as e:
        traceback.print_exc()
        # Log the exception for debugging purposes
        current_app.logger.error(f"An error occurred: {e}")
 
        # Display error message
        return jsonify({'alert_type ': 'error', 'message': 'An error occurred. Please try again.'})

 # below code is not in use 
@organization_bp.route('/display_legal_document/<filename>')
def display_legal_document(filename):
    return send_from_directory(current_app.config['ORGANIZATION_FOLDER'], filename) #return send_from_directory(current_app.config['ORGANIZATION_FOLDER'], filename): This line uses the send_from_directory function to send the file with the specified filename from the directory specified by current_app.config['ORGANIZATION_FOLDER']
#the URL for serving legal documents would be something like /display_legal_document/some_document.pdf, and it will internally use the path specified in ORGANIZATION_FOLDER, which is "static/organization_image". The client doesn't need to know the exact file system path.