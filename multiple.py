from flask import Flask, render_template, request

import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5433/login'

# Configure your PostgreSQL connection
db_config = {
    'dbname': 'login',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5433  # Change this to your desired port number
}

# Function to create a new table with a given name and a constant schema
def create_table(table_name, schema):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Construct the CREATE TABLE SQL statement with the provided table name and constant schema
         create_table_sql = "CREATE TABLE IF NOT EXISTS {} ({})".format( table_name, schema)
         cursor.execute(create_table_sql)
         conn.commit()
         return f'Table {table_name} created successfully'
    except Exception as e:
        conn.rollback()
        return f'Error: {str(e)}'
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def table():
    return render_template('multi.html')

# Route to create a table by providing a table name in the request
@app.route('/create_table', methods=['POST','GET'])
def create_custom_table():
    try:
        table_name = request.form['name']
        schema = 'id SERIAL PRIMARY KEY, name VARCHAR(255), age INT'
        result = create_table(table_name, schema)
        return result
    except Exception as e:
        return f'Error: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)
