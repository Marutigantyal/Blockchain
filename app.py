from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from flask_migrate import Migrate
import datetime
import hashlib
import json

app = Flask(__name__)
# Configure the SQLAlchemy database URI
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/blockchain'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5433/blockchain'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Define your data model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)


class Properties(db.Model):
    pro_id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    proof = db.Column(db.Integer, nullable=False)
    previous_hash = db.Column(db.String(64), nullable=False)


@app.route('/')
def home():
    with app.app_context():
        try:
            result = db.session.execute(text('SELECT version()'))
            db_version = result.scalar()  # Get the result as a scalar
            return render_template('hello.html', db_version=db_version)
        except OperationalError as e:
            # Handle the exception if the connection fails
            print(f"Database connection error: {e}")
            return render_template('index.html', db_version='Failed to retrieve database version')


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

    def proof_of_work(self,previous_proof):
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



@app.route("/mine_block", methods=["GET", "POST"])

def mine_block():
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
    
   
    response = {
        "message": "A block is MINED",
        "index": block["index"],
        "timestamp": block["timestamp"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }
    
    return jsonify(response), 200

@app.route("/get_chain", methods=["GET", "POST"])
def display_chain():
    response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
    return jsonify(response), 200

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

@app.route("/jls_extract_def", methods=["GET", "POST"])
def jls_extract_def():
    response = {"message": "Your custom message here"}  # You can customize the message
    return jsonify(response), 200



if __name__ == '__main__':
    if check_db_connection():
        print("Database connection established successfully.")
    else:
        print("Failed to establish a database connection.")
    app.run(debug=True)
