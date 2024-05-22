# init.py
import os
from flask import Flask, render_template
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
from .map import map_bp 
from altmo_utils import db 
import atexit # Close DB pool 
import json 
##db.init

_version_ = '1.0.0'


def create_app(test_config=None):
    """Initialize and create the app and return it (factory pattern)"""

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        
        app.config.from_file("config.json", load=json.load)
        
    else:
        app.config.from_mapping(test_config)

    app.secret_key = app.config.get('SECRET_KEY', 'default_secret_key')

    print("SECRET_KEY:", app.secret_key)  

    # Initialize Flask-Session after setting the secret key
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    # Set WTF_CSRF_SECRET_KEY
    app.config['WTF_CSRF_ENABLED'] = False

    # Enable CSRF protection
    app.config['CSRF_ENABLED'] = True

    app.config['UPLOAD_FOLDER'] =  app.config.get('UPLOAD_FOLDER', 'static/uploaded_images')
    
    app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = app.config.get('TRAINING_LOCATION_PICTURES_FOLDER', 'static/training_location_pictures')
   
    app.config['ORGANIZATION_FOLDER'] = app.config.get('ORGANIZATION_FOLDER', 'static/organization_image') 
    
    #app.config['ORGANIZATION_FOLDER'] = 'static/organization_image'

    app.static_folder = 'static'

    app.config["DB_URL"] = app.config.get("DATABASE_URI")

    # Initialize the database
    db.init_app(app)
    print("Database used in the project:", app.config.get("DB_URL"))

    @app.route('/')
    #@app.route('/index.html')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/privacy_note.html')
    def privacy_note():
        return render_template('privacy_note.html')
  
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