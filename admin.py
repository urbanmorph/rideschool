from flask import Flask, request, jsonify
import bcrypt
import psycopg2

app = Flask(__name__)

# Replace these variables with your actual PostgreSQL database credentials
DB_HOST = '127.0.0.1'
DB_NAME = 'Pedal_Shaale'
DB_USER = 'postgres'
DB_PASSWORD = 'root'

# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Endpoint for inserting fixed contact and hashed password into the admin table
@app.route('/insert_admin_data', methods=['POST'])
def insert_admin_data():
    try:
        data = request.get_json()
        contact = '9999999999'  # Replace this with the fixed contact number
        fixed_password = 'Pedal_shaale@2023'  # Replace this with the fixed password

        # Hash the fixed password using the hash_password function
        hashed_password = hash_password(fixed_password)

        # Connect to the PostgreSQL database
        db_connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        # Create a cursor to interact with the database
        db_cursor = db_connection.cursor()

        # Insert the fixed contact and hashed password into the admin table
        db_cursor.execute("INSERT INTO admin (contact_no, password) VALUES (%s, %s)", (contact, hashed_password))
        db_connection.commit()

        # Close the database connection and cursor
        db_cursor.close()
        db_connection.close()

        return jsonify({'message': 'Fixed contact and hashed password inserted into admin table successfully!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
