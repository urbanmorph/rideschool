from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# PostgreSQL connection details
db_host = "your_database_host"
db_name = "your_database_name"
db_user = "your_database_user"
db_password = "your_database_password"

# Function to connect to PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    return conn

# Route to render the signup form
@app.route('/')
def signup_form():
    return render_template('signup.html')

# Route to handle the form submission
@app.route('/signup', methods=['POST'])
def signup():
    contact_no = request.form['contact_no']
    password = request.form['password']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the user into the users table
        cursor.execute("INSERT INTO users (contact_no, password) VALUES (%s, crypt(%s, gen_salt('bf')))", (contact_no, password))
        conn.commit()

        cursor.close()
        conn.close()

        return "User signed up successfully!"

    except Exception as e:
        return f"Error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
