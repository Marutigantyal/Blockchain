from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5433/blockchain'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email

@app.route('/')
def index():
    # Retrieve all users from the database
    users = User.query.all()
    return render_template('index3.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Create a new user and add it to the database
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index'))

if __name__ == '__main__':
    # Create the database tables within the application context
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
