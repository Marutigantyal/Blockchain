from flask import Flask, render_template, request, redirect, url_for, send_file
import psycopg2
from io import BytesIO

app = Flask(__name__)

# Configure your PostgreSQL connection
db_config = {
    'dbname': 'login',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5433  # Change this to your desired port number
}

def create_table(table_name, schema):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Construct the CREATE TABLE SQL statement with the provided table name and constant schema
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
        cursor.execute(create_table_sql)
        conn.commit()
        return f'Table {table_name} created successfully'
    except Exception as e:
        conn.rollback()
        return f'Error: {str(e)}'
    finally:
        cursor.close()
        conn.close()
@app.route('/', methods=['GET', 'POST'])
def imageshort():
        return render_template('imageshort.html')


@app.route('/view_upload_image', methods=['GET', 'POST'])
def view_upload_image():
    if request.method == 'POST':
        # Check if the user selected "View" or "Upload" and get the table name
        action = request.form['action']
        table_name = request.form['table_name']

        # If the user selected "Upload," insert the image into the specified table
        if action == 'upload' and 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                image_data = image_file.read()
                data_type = 'image'
                query = f"INSERT INTO {table_name} (data_type, content) VALUES (%s, %s)"
                conn = psycopg2.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute(query, (data_type, image_data))
                conn.commit()
                cursor.close()
                conn.close()

        # Fetch all images from the specified table
        cursor = psycopg2.connect(**db_config).cursor()
        cursor.execute(f"SELECT id FROM {table_name}")
        image_ids = cursor.fetchall()
        cursor.close()

        return render_template('view.html', table_name=table_name, image_ids=image_ids)

    return render_template('view.html', table_name='', image_ids=[])
@app.route('/get_image/<table_name>/<int:id>')
def get_image(table_name, id):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(f"SELECT content FROM {table_name} WHERE id = %s", (id,))
    image_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if image_data:
        return send_file(BytesIO(image_data[0]), mimetype='image/jpeg')  # Adjust mimetype based on your image format

    return 'Image not found'


if __name__ == '__main__':
    app.run(debug=True)
