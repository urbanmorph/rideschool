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
from .map import map_bp 
#from map_blueprint import map_bp



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
    #####
   # app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, app.config.get('UPLOAD_FOLDER', 'static/uploaded_images'))
    app.config['UPLOAD_FOLDER'] =  app.config.get('UPLOAD_FOLDER', 'static/uploaded_images')
    #app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = os.path.join(app.instance_path, app.config.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/t_l_pictures'))
    app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = app.config.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/training_location_pictures')
    #app.config['ORGANIZATION_FOLDER'] = os.path.join(app.instance_path, app.config.get('ORGANIZATION_FOLDER', 'static/organization_image'))
    app.config['ORGANIZATION_FOLDER'] = app.config.get('ORGANIZATION_FOLDER', 'static/organization_image')
    # Update this line in create_app function
    #app.config['ORGANIZATION_FOLDER'] = 'static/organization_image'

    app.static_folder = 'static'

    # Set DB_URL directly in app.config
    app.config["DB_URL"] = app.config.get("DATABASE_URI")

 # Initialize the database
    db.init_app(app)
    print("Database used in the project:", app.config.get("DB_URL"))




    @app.route('/')
    #@app.route('/index.html')
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
    app.register_blueprint(map_bp) 
     # Close DB pool before exiting the app
    atexit.register(db.close_db_pool)
    return app

rideschool_app = create_app()
