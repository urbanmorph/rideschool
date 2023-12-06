print("import feane/ summary.py")
from flask import Blueprint, render_template
##import psycopg2
#from .config.config import get_config_value   # Import your configuration function
#from altmo_utils.db  import get_db_connection 
from altmo_utils.db import get_db_cursor
import traceback
summary_bp = Blueprint('summary', __name__)

# Initialize db_connection to None initially
##db_connection = None

##def get_db_connection():
  ##  global db_connection
    ##if db_connection is None:
        # PostgreSQL database connection
      ##  db_connection = psycopg2.connect(
        ##    host=get_config_value('db_host'),
          ##  database=get_config_value('db_name'),
            ##user=get_config_value('db_user'),
           ## password=get_config_value('db_password')
        ##)
    ##return db_connection

@summary_bp.route('/summary')
def summary():
    # Get a database connection
    with get_db_cursor() as cursor:
    #with get_db_connection() as db_connection:
        if cursor is None:
            return "Failed to get a database cursor"

        try:
           # cursor = db_connection.cursor()

        # Calculate the statistics from the database
            cursor.execute("SELECT COUNT(*) FROM users_signup WHERE role = 'trainer'")
            #total_trainers = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_trainers =result.get('count', 0)
            #total_trainers = result['count'] if (result is not None) else 0
            print(result)

            cursor.execute("SELECT COUNT(*) FROM users_signup WHERE role = 'participant'")
            #total_participants = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_participants = result.get('count', 0)
            print(result)

            cursor.execute("SELECT COUNT(*) FROM participants WHERE participant_status IN ('COMPLETED', 'CERTIFIED')")
            #total_completed_certified = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_completed_certified = result.get('count', 0)
            print(result)

            cursor.execute("SELECT COUNT(*) FROM participants WHERE participant_status = 'ONGOING'")
            #total_ongoing = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_ongoing = result.get('count', 0)
            print(result)

            cursor.execute("SELECT COUNT(*) FROM participants WHERE participant_status = 'DROP-OUT'")
            #total_dropouts = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_dropouts = result.get('count', 0)
            print(result)


            cursor.execute("SELECT COUNT(*) FROM participants WHERE participant_status = 'NEW'")
            #total_uncontacted = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_uncontacted= result.get('count', 0)
            print(result)

        except Exception as e:
            traceback.print_exc()
        # Handle any exceptions (e.g., database errors)
            return "Error: " + str(e)
    ##finally:
      ##  cursor.close()
    
    return render_template('summary.html', 
        total_trainers=total_trainers, 
        total_participants=total_participants,
        total_completed_certified=total_completed_certified,
        total_ongoing=total_ongoing,
        total_dropouts=total_dropouts,
        total_uncontacted=total_uncontacted)
