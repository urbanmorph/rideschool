# your_app/__init__.py

import os
from flask import Flask
from flask_session import Session
from .admin import admin_bp
from .logins import logins_bp
from .participant import participant_bp
from .sessions import sessions_bp
from .signup import signup_bp
from .summary import summary_bp
from .trainer import trainer_bp
from .training_locations_list import training_locations_list_bp
from .organization import organization_bp
#from .db import init_app, DB_URL
from altmo_utils import db

_version_ = '1.0.0'

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from the instance folder
    app.config.from_pyfile('config.py', silent=True)

    # Set the secret key using the same name
    app.secret_key = app.config.get('SECRET_KEY', 'default_secret_key')

    # Initialize Flask-Session after setting the secret key
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    # Set WTF_CSRF_SECRET_KEY
    app.config['WTF_CSRF_ENABLED'] = False

    # Enable CSRF protection
    app.config['CSRF_ENABLED'] = True

    # Set the upload folder configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, app.config.get('UPLOAD_FOLDER', 'static/uploaded_images'))
    app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = os.path.join(app.instance_path, app.config.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/t_l_pictures'))
    app.config['ORGANIZATION_FOLDER'] = os.path.join(app.instance_path, app.config.get('ORGANIZATION_FOLDER', 'static/organization_image'))
    app.static_folder = 'static'

     # Set DB_URL directly in app.config
    app.config["DB_URL"] = app.config.get("DATABASE_URI")

    # Register your form with the app
    db.init_app(app)  # This sets the database URL
    print("Database used in the project:", app.config.get("DB_URL"))

   # print("Database used in the project:", DB_URL)

    # Register blueprints
    app.register_blueprint(participant_bp)
    app.register_blueprint(trainer_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(logins_bp)
    app.register_blueprint(training_locations_list_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(organization_bp)

    return app
########


# init.py

import os
from flask import Flask, render_template
from flask_session import Session
#from .database import init_db
from .config.config import load_config
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
##from .db import init_app, DB_URL

from altmo_utils import db
##db.init




# In your __init__.py, the create_app function sets up the Flask application




_version_ = '1.0.0'

def create_app(config_filename='config.py'):
    app = Flask(__name__)

    # Load configuration from the config.txt file
    config_dict = load_config(os.path.join(os.path.dirname(__file__), 'config', 'config.txt'))
    print("config dict:", config_dict)
    # Set the secret key using the same name
    app.secret_key = config_dict.get('SECRET_KEY', 'default_secret_key')
    print("SECRET_KEY:", app.secret_key)  # Print the SECRET_KEY for debugging
####
    # Set the keys from config_dict into app.config
    for key, value in config_dict.items():
        app.config[key] = value
####
    # Initialize Flask-Session after setting the secret key
    app.config['SESSION_TYPE'] = 'filesystem'

    # Initialize Flask-Session after setting the secret key
    Session(app)




    # Set WTF_CSRF_SECRET_KEY
    app.config['WTF_CSRF_ENABLED'] = False

    # Enable CSRF protection
    app.config['CSRF_ENABLED'] = True

    # Set the upload folder configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), config_dict.get('UPLOAD_FOLDER', 'static/uploaded_image'))
    app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = os.path.join(os.path.dirname(__file__), config_dict.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/training_location_pictures'))
    app.config['ORGANIZATION_FOLDER'] = os.path.join(os.path.dirname(__file__), config_dict.get('ORGANIZATION_FOLDER', 'static/organization_image'))
    app.static_folder = 'static'
    #app.config['STATIC_FOLDER'] = 'static'






    @app.route('/index.html')
    def index():
        return render_template('index.html')

    @app.route('/FAQ.html')
    def about():
        return render_template('FAQ.html')

    # Initialize and register blueprints
    db.init_app(app)  # This sets the database URL

    # Import DB_URL after calling init_app
    
    print("data base used in the project", DB_URL)

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

    #atexit.register(db.close_db_pool)
    return app





@organization_bp.route('/submit_organization', methods=['POST'])
def submit_organization():
    try:
        # ... (Your existing code)

        # Retrieve form data
        coordinator_contact = request.form['coordinator-contact']

        # ... (Your existing code)

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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                coordinator_contact  # Add the new field here
            ))

        # ... (Your existing code)

    except Exception as e:
        # ... (Your existing code)



<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organization Form</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            
            background-color: #f4f4f4;
        }

        h1 {
            margin-bottom: 20px;
            color: #333;
            text-align: center;
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        }

        form {
        max-width: 500px;
        margin: 0 auto;
        padding: 40px;
        border-radius: 5px;
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
    }

       

        label {
            font-weight: bold;
        }

        input[type="text"],
        input[type="email"],
        input[type="tel"],
        select,
        textarea,
        input[type="file"] {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            width: 95%;
            margin-bottom: 10px;
        }

        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .error-message {
            color: #FF0000;
            margin-top: 5px;
            display: none;
        }

        .alert {
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 4px;
        }

        .alert-success {
            background-color: #D4EDDA;
            border: 1px solid #C3E6CB;
            color: #155724;
        }

        .alert-danger {
            background-color: #F8D7DA;
            border: 1px solid #F5C6CB;
            color: #721C24;
        }
        form button {
        padding: 10px 20px;
        background-color: #4CAF50;
        color: #fff;
        border: none;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    form button:hover {
        background-color: #45a049;
    }
    
    </style>

<style>
    /* Your existing styles */

    .alert-success {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
    }

    .alert-danger {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        color: #721C24;
    }
</style>
</head>
<body>
    {% include 'navbar.html' %}
    <br>
    <br>
    <br>
    <br>
    <br>
    <div class="container">
        <h1>Organization Form</h1>

        <form id="organization-form" action="/submit_organization" method="post" enctype="multipart/form-data">
            <label for="organization-name">Organization Name:</label>
            <input type="text" id="organization-name" name="organization-name" required>
            
            <label for="organization-address">Organization Address:</label>
            <input type="text" id="organization-address" name="organization-address" required>
            
            <label for="organization-contact">Organization Contact:</label>
            <input type="text" id="organization-contact" name="organization-contact" required>
            <div class="error-message" id="contact-error-message"></div>
            
            <label for="organization-email">Organization Email:</label>
            <input type="email" id="organization-email" name="organization-email" required>
            <div class="error-message" id="email-error-message"></div>
            
            <label for="organization-type">Organization Type:</label>
            <select id="organization-type" name="organization-type" required>
                <option value="" selected disabled>Select Organization Type</option>
                <option value="Public Limited Company">Public Limited Company</option>
                <option value="Private Limited Company">Private Limited Company</option>
                <option value="Registered Trust">Registered Trust</option>
                <option value="Registered Society">Registered Society</option>
                <option value="Registered Resident Welfare Association (RWA)">Registered Resident Welfare Association (RWA)</option>
                <option value="Section 8 Company">Section 8 Company</option>
                <option value="New Governmental Organization">New Governmental Organization</option>
                <option value="Other">Other</option>
            </select>
            
            <label for="organization-activities">Organization Activities:</label>
            <textarea id="organization-activities" name="organization-activities"></textarea>
            
            <label for="organization-legal-status-document">Legal Status Document:</label>
            <input type="file" id="organization-legal-status-document" name="organization-legal-status-document" accept=".pdf,.doc,.docx">
            
            <label for="coordinator-name">Coordinator Name:</label>
            <input type="text" id="coordinator-name" name="coordinator-name" required>
            
            <label for="coordinator-email">Coordinator Email:</label>
            <input type="email" id="coordinator-email" name="coordinator-email" required>

            <label for="coordinator-contact">Coordinator Contact:</label>
<input type="text" id="coordinator-contact" name="coordinator-contact" required>
            
            <button type="submit">Submit</button>
        </form>

        <div class="alert" id="messageAlert" style="display: none;"></div>

        <script>
            document.addEventListener('DOMContentLoaded', function () {
                var organizationForm = document.getElementById('organization-form');

                organizationForm.addEventListener('submit', async function (event) {
                    event.preventDefault();

                    // Validate form using HTML5 built-in validation
                    if (!this.checkValidity()) {
                        return;
                    }

                    const formData = new FormData(this);

                    try {
                        const response = await fetch('/submit_organization', {
                            method: 'POST',
                            body: formData,
                        });

                        const result = await response.json();

                        if (result.status === 'success') {
                            displayMessage('alert-success', result.message);
                            // Additional logic after successful form submission
                        } else if (result.status === 'error') {
                            displayMessage('alert-danger', result.message);
                        }
                    } catch (error) {
                        displayMessage('alert-danger', 'An error occurred. Please try again.');
                    }
                });

                function displayMessage(type, message) {
                    var messageAlert = document.getElementById('messageAlert');
                    messageAlert.innerHTML = '<div class="alert ' + type + '">' + message + '</div>';
                    messageAlert.style.display = 'block';
                }
            });
        </script>
    </div>
</body>
</html>
