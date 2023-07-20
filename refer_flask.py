from flask import Flask
import psycopg2

app = Flask(_name_)

# Configure the PostgreSQL connection
def get_data_from_database():
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="Pedal_Shaale",
        user="postgres",
        password="root"
    )
    cursor = conn.cursor()



    # Execute a query to fetch the data
    cursor.execute('SELECT * FROM participants')

    # Fetch all rows from the result set
    rows = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    return rows

data = get_data_from_database()
for row in data:
    print(row)  # Print each row in the terminal
    
    

@app.route('/table')
def home():
    try:
        data = get_data_from_database() #function
        return render_template('participant_table.html', data=data)
    except Exception as e:
        traceback.print_exc()
        return "An error occurred while retrieving data from the database."

if _name_ == '_main_':
    app.run(debug=False)