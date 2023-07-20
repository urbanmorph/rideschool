from flask import Flask, render_template
from participant import participant_bp
from trainer import trainer_bp
from sessions import sessions_bp
import os

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DATABASE'] = 'Pedal_Shaale'
app.config['UPLOAD_FOLDER'] = 'static/uploaded_image'

# Set the static folder for CSS, JS, and images
app.static_folder = 'static'

# Home page
@app.route('/index.html')
def home():
    return render_template('index.html')

# About page
@app.route('/about.html')
def about():
    return render_template('about.html')

# Register the participant blueprint
app.register_blueprint(participant_bp)

# Register the trainer blueprint
app.register_blueprint(trainer_bp)

# Register the sessions blueprint with the app
app.register_blueprint(sessions_bp)

if __name__ == '__main__':
    from sessions import create_database, init_db
    create_database()
    init_db()
    app.run(debug=True)
