print("import feane/ summary.py")
from flask import Blueprint, render_template
from altmo_utils.db import get_db_cursor
import traceback
summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/summary')
def summary():
    # Get a database connection
    with get_db_cursor() as cursor:
    
        if cursor is None:
            return "Failed to get a database cursor"
        try:
            
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

            cursor.execute("SELECT COUNT(*) FROM participants WHERE status IN ('COMPLETED', 'CERTIFIED')")
            #total_completed_certified = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_completed_certified = result.get('count', 0)
            print(result)

            cursor.execute("SELECT COUNT(*) FROM participants WHERE status = 'ONGOING'")
            #total_ongoing = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_ongoing = result.get('count', 0)
            print(result)

            cursor.execute("SELECT COUNT(*) FROM participants WHERE status = 'DROP-OUT'")
            #total_dropouts = cursor.fetchone()[0]
            result = cursor.fetchone()
            total_dropouts = result.get('count', 0)
            print(result)

            cursor.execute("SELECT COUNT(*) FROM participants WHERE status = 'NEW'")
            #cursor.execute("SELECT COUNT(*) FROM participants WHERE participant_status = 'NEW'")
            result = cursor.fetchone()
            total_uncontacted= result.get('count', 0)
            print(result)

            # Calculate the total number of training_location_address
            cursor.execute("SELECT COUNT(*) FROM training_locations_list")
            result = cursor.fetchone()
            total_training_location_address = result.get('count', 0)
            # Subtract 1 from the total count
            total_training_location_address -= 1 
        except Exception as e:
            traceback.print_exc()
        # Handle any exceptions (eg: database errors)
            return "Error: " + str(e)
    
    return render_template('summary.html', 
        total_trainers=total_trainers, 
        total_participants=total_participants,
        total_completed_certified=total_completed_certified,
        total_ongoing=total_ongoing,
        total_dropouts=total_dropouts,
        total_uncontacted=total_uncontacted,
        total_training_location_address=total_training_location_address)
