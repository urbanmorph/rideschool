import os

# config.py


def load_config(relative_path_to_config):
    config_dict = {}  

    with open(relative_path_to_config, 'r') as config_file:
        for line in config_file:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                config_dict[key] = value

    print("Keys loaded from config.txt:", config_dict.keys())
    return config_dict






# Dynamically generate the path to config.txt using a relative path
relative_path_to_config = os.path.join(os.path.dirname(__file__), 'config.txt')

# Print the current working directory and the dynamically generated relative path to config.txt
print("Current working directory:", os.getcwd())
print("Relative path to config.txt:", relative_path_to_config)

DEBUG = False  # Set to False in production

SECRET_KEY = 'Pedal_Shaale@2023' # Set your secret key here to maintain the sessions security 
SESSION_TYPE = 'filesystem'
DATABASE_URI = f"postgresql://postgres:root@127.0.0.1:5432/Pedal_Shaale"
#DATABASE_URI = f"postgresql://postgres:root@127.0.0.1:5432/Pedal_Shaale?password=root"
#DATABASE_URI = f"postgresql://postgres@127.0.0.1:5432/Pedal_Shaale"
#DATABASE_URI = f"postgresql://postgres:root@localhost:5432/Pedal_Shaale"
#DATABASE_URI = f"postgresql://postgres@localhost:5432/Pedal_Shaale"


ORGANIZATION_IMAGE = 'static/organization_image'
UPLOAD_FOLDER = 'static/uploaded_images'
TRAINING_LOCATION_PICTURES_FOLDER = 'static/t_l_pictures'

config_dict = load_config(relative_path_to_config)

# Function to access configuration values
def get_config_value(key, default=None):
    return config_dict.get(key, default)
