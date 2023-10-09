from flask import Flask, render_template
from logins import logins_bp  
from flask_session import Session
import os
from participant import participant_bp
from trainer import trainer_bp
from sessions import sessions_bp
from signup import signup_bp
from training_locations_list import training_locations_list_bp




app = Flask(__name__)
app.config['SECRET_KEY'] = 'Pedal_Shaale@2023'  # Set your secret key here to maintain the sessions security 
app.config['SESSION_TYPE'] = 'filesystem' # Configure the app to use sessions

Session(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DATABASE'] = 'Pedal_Shaale'
app.config['UPLOAD_FOLDER'] = 'static/uploaded_image'
# Update the 'TRAINING_LOCATION_PICTURES_FOLDER' to the new path


# Set the path for uploaded images
app.config['TRAINING_LOCATION_PICTURES_FOLDER'] = 'static/t_l_picture'



app.secret_key = os.urandom(24)  # Generate a random secret key
# Ensure Flask serves static files correctly
app.static_folder = 'static'

@app.route('/index.html')
def index():
    return render_template('index.html')



# About page
@app.route('/FAQ.html')
def about():
    return render_template('FAQ.html')

# Register the participant blueprint
app.register_blueprint(participant_bp)

# Register the trainer blueprint
app.register_blueprint(trainer_bp)



# Register the sessions blueprint with the app
app.register_blueprint(sessions_bp)

# Register the signup blueprint with the app
app.register_blueprint(signup_bp)



# Register your blueprint
app.register_blueprint(logins_bp)


# Register the training locations Blueprint


app.register_blueprint(training_locations_list_bp)






if __name__ == '__main__':
    from sessions import create_database
    create_database()
   

    app.run(debug=True)