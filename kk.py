from flask import Flask, render_template, request, redirect, url_for, send_file
import psycopg2
from io import BytesIO

app = Flask(__name__)

# PostgreSQL database configuration
db_connection = psycopg2.connect(
    dbname="login",
    user="postgres",
    password="1234",
    host="localhost",
    port="5433"
)

@app.route('/')
def index():
    return render_template('ii.html')

@app.route('/view_data', methods=['GET', 'POST'])
def view_data():
    if request.method == 'POST':
        # Fetch data based on the selected type (image or text)
        data_type = request.form['data_type']
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM my_data WHERE data_type = %s", (data_type,))
        data = cursor.fetchall()
        cursor.close()
        return render_template('view_data.html', data=data)
    return redirect(url_for('index'))

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename != '':
            # Read the image file and store it in the database
            image_data = image_file.read()
            data_type = 'image'
            cursor = db_connection.cursor()
            cursor.execute("INSERT INTO my_data (data_type, content) VALUES (%s, %s)", (data_type, image_data))
            db_connection.commit()
            cursor.close()
    return redirect(url_for('index'))


@app.route('/get_image/<int:id>')
def get_image(id):
    cursor = db_connection.cursor()
    cursor.execute("SELECT content FROM my_data WHERE id = %s", (id,))
    image_data = cursor.fetchone()
    cursor.close()

    if image_data:
        return send_file(BytesIO(image_data[0]), mimetype='image/jpeg')  # Adjust mimetype based on your image format

    return 'Image not found'
@app.route('/delete_image/<int:id>', methods=['POST'])
def delete_image(id):
    # Delete the image with the specified ID from the database
    # Add your code here to delete the image
    # ...
    flash(f'Image with ID {id} has been deleted', 'success')
    return redirect(url_for('view_data'))


if __name__ == '__main__':
    app.run(debug=True)
