# init.py

import os
from flask import Flask, render_template
from flask_session import Session
#from .database import init_db
#from .config.config import load_config
from .admin import admin_bp
from .logins import logins_bp
from .participant import participant_bp
from .sessions import sessions_bp
from .signup import signup_bp
from .summary import summary_bp
from .trainer import trainer_bp
from .training_locations_list import training_locations_list_bp
from .organization import organization_bp
#####from .db import DB_URL
#from .db import init_app, DB_URL
#from .altmo_utils import db

from altmo_utils import db 
import atexit # Close DB pool 
import json 
##db.init

# In your __init__.py, the create_app function sets up the Flask application

_version_ = '1.0.0'


def create_app(test_config=None):
    """Initialize and create the app and return it (factory pattern)"""

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        #config_path = os.path.join(app.instance_path, 'config.json')

       
        #config_path = os.path.join(app.instance_path, 'config.json')
        #app.config.from_json(config_path)
        #_app.config.from_pyfile("config.py", silent=True)
        app.config.from_file("config.json", load=json.load)
        
    else:
        app.config.from_mapping(test_config)

##def create_app(config_filename='config.py'):
    ##app = Flask(__name__)
#####def create_app():
   ##### app = Flask(__name__, instance_relative_config=True)
      # Load configuration from the instance folder
    ######app.config.from_pyfile('config.py', silent=True)
    # Set the secret key using the same name
    app.secret_key = app.config.get('SECRET_KEY', 'default_secret_key')

   
    # Load configuration from the config.txt file
    ##config_dict = load_config(os.path.join(os.path.dirname(__file__), 'config', 'config.txt'))
    ##print("config dict:", config_dict)
    # Set the secret key using the same name
    ##app.secret_key = config_dict.get('SECRET_KEY', 'default_secret_key')
    print("SECRET_KEY:", app.secret_key)  # Print the SECRET_KEY for debugging
####
    # Set the keys from config_dict into app.config
    ##for key, value in config_dict.items():
     ##   app.config[key] = value
####
    # Initialize Flask-Session after setting the secret key
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)




    # Set WTF_CSRF_SECRET_KEY
    app.config['WTF_CSRF_ENABLED'] = False

    # Enable CSRF protection
    app.config['CSRF_ENABLED'] = True

    # Set the upload folder configuration
    ##app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), config_dict.get('UPLOAD_FOLDER', 'static/uploaded_image'))
    ##app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = os.path.join(os.path.dirname(__file__), config_dict.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/training_location_pictures'))
    ##app.config['ORGANIZATION_FOLDER'] = os.path.join(os.path.dirname(__file__), config_dict.get('ORGANIZATION_FOLDER', 'static/organization_image'))
    ##app.static_folder = 'static'
    #app.config['STATIC_FOLDER'] = 'static'
    # Set the upload folder configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, app.config.get('UPLOAD_FOLDER', 'static/uploaded_images'))
    app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = os.path.join(app.instance_path, app.config.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/t_l_pictures'))
    app.config['ORGANIZATION_FOLDER'] = os.path.join(app.instance_path, app.config.get('ORGANIZATION_FOLDER', 'static/organization_image'))
    # Update this line in create_app function
    #app.config['ORGANIZATION_FOLDER'] = 'static/organization_image'

    app.static_folder = 'static'

    # Set DB_URL directly in app.config
    app.config["DB_URL"] = app.config.get("DATABASE_URI")

 # Initialize the database
    db.init_app(app)
    print("Database used in the project:", app.config.get("DB_URL"))




    @app.route('/index.html')
    def index():
        return render_template('index.html')

    @app.route('/FAQ.html')
    def about():
        return render_template('FAQ.html')

    # Initialize and register blueprints
    ##db.init_app(app)  # This sets the database URL

    # Import DB_URL after calling init_app
    
    #print("data base used in the project", DB_URL)

    # Register your form with the app
   
    app.register_blueprint(participant_bp)
    app.register_blueprint(trainer_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(logins_bp)
    app.register_blueprint(training_locations_list_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(organization_bp)

     # Close DB pool before exiting the app
    atexit.register(db.close_db_pool)
    return app




# organization.py

print("import feane/ organization.py")

from flask import Blueprint, render_template, request, current_app, send_from_directory, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
#from .db import get_db_cursor
from altmo_utils.db import get_db_cursor
from flask import current_app
import os
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
        legal_status_document = request.files['organization-legal-status-document']
        file_path = None

        #if legal_status_document:
            # Generate a unique filename using UUID and save to the upload folder
         #   filename = str(uuid.uuid4()) + secure_filename(legal_status_document.filename)
          #  file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename)
           # legal_status_document.save(file_path)
        if legal_status_document:
            # Ensure the directory exists
            if not os.path.exists(current_app.config['ORGANIZATION_FOLDER']):
                os.makedirs(current_app.config['ORGANIZATION_FOLDER'])
##############
            original_filename = secure_filename(legal_status_document.filename)
            filename = str(uuid.uuid4()) + '_' + original_filename
            # Generate a unique filename using UUID and save to the upload folder
            #filename = str(uuid.uuid4()) + secure_filename(legal_status_document.filename)
            #file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename)
            ##file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename.replace('/', '\\'))
            # Print the generated file path for debugging
            file_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], filename)
            file_path = file_path.replace('/', os.path.sep)
            print("Generated file path:", file_path)

            legal_status_document.save(file_path)


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
                file_path,
                coordinator_name,
                coordinator_email,
                coordinator_contact
            ))

        # Display success message
        message = f"Organization {organization_name} submitted successfully!"
        return jsonify({'status': 'success', 'message': message})

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"An error occurred: {e}")

        # Display error message
        return jsonify({'status': 'error', 'message': 'An error occurred. Please try again.'})


##@organization_bp.route('/organization_image/<filename>')
##def display_image(filename):
  ##  return send_from_directory(current_app.config['ORGANIZATION_FOLDER'], filename)

##"D:\job\urban_morph\pedal_shaale_project\altmo_rideschool\static\organization_image"

@organization_bp.route('/organization_image/<filename>')
def display_image(filename):
    relative_path = filename.replace(os.path.sep, '/').split(os.path.sep)[-1]
    full_path = os.path.join(current_app.config['ORGANIZATION_FOLDER'], relative_path)
    return send_from_dire