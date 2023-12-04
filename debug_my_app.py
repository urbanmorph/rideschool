
# debug_my_app.py
import os

print("Current working directory:", os.getcwd())

from werkzeug.serving import run_simple
from altmo_rideschool import create_app

import logging

import sys


root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_path)


print('here')
if __name__ == "__main__":
    app = create_app()
    app.logger.setLevel(logging.DEBUG)
    print("Starting the development server ")
    run_simple("localhost", 5000, app, use_reloader=True)
    