
from flask import Flask, render_template, request, redirect, url_for, jsonify,flash,send_file,flash,Response
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session
from flask_session import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from flask_migrate import Migrate
import datetime
import hashlib
import json
from flask_wtf import FlaskForm  # Add this import
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
import psycopg2
from io import BytesIO
from sqlalchemy import desc
import mimetypes  # Import the mimetypes module

 



app= Flask(__name__)
# Configure the SQLAlchemy database URI
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/blockchain'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/login'
app.config['SECRET_KEY'] = 'Martin'
#session 
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)



##########################      Define your data model         ###############################
class Product(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)


class Properties(db.Model):
    pro_id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    proof = db.Column(db.Integer,unique=True, nullable=False)
    previous_hash = db.Column(db.String(64), nullable=False)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
class up(db.Model):
    number = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    proof = db.Column(db.Integer, db.ForeignKey('properties.proof'), nullable=False)

###################################          create   ##########################3
@app.route('/create', methods=['GET', 'POST'])
def create():
    pp = session.get('proof')
    use= Users.query.order_by(Users.id.desc()).with_entities(Users.username).first() # Assuming you have a form field for username
    username = ', '.join(use)
    
    new_user = up(username=username, proof=pp)

    # Add the User instance to the session
    db.session.add(new_user)

    # Commit the transaction to save the new user to the database
    db.session.commit()
    return "done"


    
@app.route('/homep')
def homep():
    return render_template('index.html')







#home page________________________________________________________________________________________________
@app.route('/')
def home():
    with app.app_context():
        try:
            result = db.session.execute(text('SELECT version()'))
            db_version = result.scalar()  # Get the result as a scalar
            return render_template('index.html', db_version=db_version)
        except OperationalError as e:
            # Handle the exception if the connection fails
            print(f"Database connection error: {e}")
            return render_template('hello.html', db_version='Failed to retrieve database version')


def check_db_connection():
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            return True
        except OperationalError as e:
            print(f"Database connection error: {e}")
            return False




@app.route('/add_product', methods=['GET'])
def add_product_page():
    return render_template('add_product.html')


@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))

        # Create a new product and add it to the database
        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('add_product_page'))

    
## ========================================================= ##
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash="0")

    def create_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.chain.append(block)
        return block

    def print_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof * 2 - previous_proof * 2).encode()
            ).hexdigest()
            if hash_operation[:5] == "00000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != self.hash(previous_block):
                return False
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = hashlib.sha256(
                str(proof * 2 - previous_proof * 2).encode()
            ).hexdigest()
            if hash_operation[:5] != "00000":
                return False
            previous_block = block
            block_index += 1
        return True

blockchain = Blockchain()

#############################     mine_block       ##############################

@app.route('/mine_block', methods=['GET', 'POST'])
def mine_block():
    if request.method == 'POST':
        previous_block = blockchain.print_previous_block()
        previous_proof = Properties.query.order_by(Properties.pro_id.desc()).first().proof if Properties.query.count() > 0 else 0
        proof = blockchain.proof_of_work(previous_proof)
        previous_hash = blockchain.hash(previous_block)
        block = blockchain.create_block(proof, previous_hash)

        new_block = Properties(
            index=block["index"],
            timestamp=block["timestamp"],
            proof=block["proof"],
            previous_hash=block["previous_hash"],
        )
        db.session.add(new_block)
        db.session.commit()
        session['proof'] = proof
        return str(proof)  # Return the proof value
    
     
@app.route("/get_chain", methods=["GET", "POST"])
def display_chain():
    response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
    return jsonify(response), 200
@app.route("/block", methods=['GET'])
def check_block(block_number):
    # Query the database to check if the block number exists
    block = Properties.query.filter_by(block_number=block_number).first()
    
    if block:
        # Block number exists in the database
        response = {'message': f'Block number {block_number} exists in the database.'}
        return jsonify(response), 200
    else:
        # Block number does not exist in the database
        response = {'message': f'Block number {block_number} does not exist in the database.'}
        return jsonify(response), 404
@app.route("/new", methods=["GET", "POST"])
def new():
    return render_template('newuser.html')

@app.route("/hel",methods=["POST"])
def news():
    return render_template('index.html')



####################3       newuser       ##################____

@app.route('/newuser', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if the email already exists
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'error')
        else:
            k=username
            new_user = Users(username=username, email=email, password=password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully!', 'success')
                result = mine_block()  # Get the proof value
                if result != 0:
                    result1 = create()
                    print("helloooo")
                    schema = 'id SERIAL PRIMARY KEY, data_type character varying(255) NOT NULL, content bytea NOT NULL'
                    m = create_tableh(k,schema)
                    print(m)

                else:
                    print("not working")


                return render_template('blockin.html', result=result, username=username)

            except IntegrityError:
                db.session.rollback()
                flash('Username already exists!', 'error')

    return render_template('newuser.html')



db_config = {
    'dbname': 'login',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5432  # Change this to your desired port number
}


def create_tableh(table_name, schema):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Construct the CREATE TABLE SQL statement with the provided table name and constant schema
         create_table_sql = "CREATE TABLE IF NOT EXISTS {} ({})".format( table_name, schema)
         cursor.execute(create_table_sql)
         conn.commit()
         
    except Exception as e:
        conn.rollback()
        return f'Error: {str(e)}'
    finally:
        cursor.close()
        conn.close()



# Route to create a table by providing a table name in the request



@app.route("/search_block", methods=["GET", "POST"])
def search_block():
    if 'proof' == 5:
        response = {"message": "blockchain is found"}
        return jsonify(response), 200
    else:
        response = {"message": "blockchain not found"}
        return jsonify(response), 200

@app.route("/valid", methods=["GET", "POST"])
def valid():
    valid = blockchain.chain_valid(blockchain.chain)
    if valid:
        response = {"message": "The Blockchain is valid."}
    else:
        response = {"message": "The Blockchain is not valid."}
    return jsonify(response), 200

@app.route('/admin')
def admin():
    return render_template('hello.html')


#########################         login        ##############################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username= request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Try to find the user by username or email
        userc = Users.query.filter(
            (Users.username == username) &
            (Users.email == email) &
            (Users.password == password)
        ).first()
        if userc:
            # Successful login
            flash('Login successful', 'success')
            session['username'] = username
            # Implement your login logic here, e.g., setting a session variable
            return render_template('add.html')
        else:
            # Failed login
            flash('Invalid credentials. Please try again.', 'error')

     # Create an HTML template for your login page

    return render_template('index.html')


@app.route('/blockkey', methods=['GET', 'POST'])
def blockkey():
   if request.method == 'POST':
        user = session.get('username')  # Use session.get() to avoid KeyError
        blockid = request.form.get('blockid')  # Get blockid from the form data
        yes = up.query.filter_by(proof=blockid).first()
        y = yes.username
        if y==user:
            # Query the database to retrieve the username based on the blockid
            session['username'] = user
            return redirect(url_for('view', blockid=blockid))
            
        else:
            # Handle the case where blockid is not provided
            yes = None

        return render_template('index.html')
    
   


db_connection = psycopg2.connect(
    dbname="login",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

######################### view_data           ##############################
@app.route('/view_data/<table_name>', methods=['GET', 'POST'])
def view_data(table_name):
    if request.method == 'POST':
        session['table_name'] = table_name
        session['image_id'] = id
        # Get the table name and data type from the form
        data_type = request.form['data_type']
        cursor = db_connection.cursor()
        #cursor.execute("SELECT * FROM {table_name} WHERE data_type = %s", (data_type,))
        cursor.execute(f"SELECT id FROM {table_name} WHERE data_type = %s", ('image',))

        data = cursor.fetchall()
        cursor.close()
       
        
        return render_template('view_data.html', table_name=table_name,data=data,)

    return redirect(url_for('view'))

#######################  upload_image         ################################

@app.route('/upload_image/<table_name>', methods=['POST'])
def upload_image(table_name):
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename != '':
            # Read the image file and store it in the specified table
            image_data = image_file.read()
            data_type = 'image'

            # Construct the SQL query dynamically with the provided table name
            query = f"INSERT INTO {table_name} (data_type, content) VALUES (%s, %s)"

            cursor = db_connection.cursor()
            cursor.execute(query, (data_type, image_data))
            db_connection.commit()
            cursor.close()
    return redirect(url_for('view'))

########################        veiw  ################################
@app.route('/view', methods=['GET','POST'])
def view():

    blockid = request.args.get('blockid')  # Get blockid from query parameter
    if blockid:
        result = up.query.filter_by(proof=blockid).first()
        username = result.username
        session['table_name'] = username
    else:
        username = session.get('table_name')
    if username:
        # Process the blockid as needed
        return render_template('ii.html', hh=username)
    else:
        # Handle the case where blockid is not provided
        return render_template('ii.html')
####################   get_image ##########################

@app.route('/get_image')
def get_image():
    table_name = request.args.get('table_name')
    id = request.args.get('id')

    print(f"Table Name: {table_name}")
    print(f"Image ID: {id}")

    if table_name and id:
        try:
            id = int(id)
        except ValueError:
            return 'Invalid Image ID'

        cursor = db_connection.cursor()
        cursor.execute(f"SELECT content FROM {table_name} WHERE id = %s", (id,))
        image_data = cursor.fetchone()
        cursor.close()

        if image_data:
            return Response(image_data[0], content_type='image/jpeg')  # ✅ FIX

    return 'Image not found'

@app.route("/jls_extract_def", methods=["GET", "POST"])
def jls_extract_def():
    response = {"message": "Your custom message here"}  # You can customize the message
    return jsonify(response), 200



if __name__ == '__main__':
    if check_db_connection():
        print("Database connection established successfully.")
    else:
        print("Failed to establish a database connection.")
    with app.app_context():
        db.create_all()
    app.run(debug=True)