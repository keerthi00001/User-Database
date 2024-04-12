import secrets
import string
import re
import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Generate a random secret key
def generate_secret_key(length=32):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

# Set the secret key for the application
app.secret_key = generate_secret_key()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['WebUsers']  # Replace 'your_database' with the name of your database
users_collection = db['users']  # Collection to store user details

# Dictionary to store user information
user_data = {}

def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@srmist\.edu\.in$'
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        reg_number = request.form['reg_number']
        department = request.form['department']
        course = request.form['course']
        year = request.form['year']
        
        # Validate email pattern
        if not validate_email(email):
            return 'Invalid email address. Please enter a valid SRMIST email address.'
        
        # Store data in session variables
        session['email'] = email
        session['reg_number'] = reg_number
        session['department'] = department
        session['course'] = course
        session['year'] = year
        
        # Store user data in dictionary with key as every character before '@' symbol in email
        username = email.split('@')[0]  # Extract username from email
        user_data[username] = {
            'email': email,
            'reg_number': reg_number,
            'department': department,
            'course': course,
            'year': year,
            'login_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Store user details in MongoDB collection
            users_collection.insert_one(user_data[username])
        except Exception as e:
            return f'Error inserting document into MongoDB: {str(e)}'
        
        return redirect(url_for('success'))

@app.route('/success')
def success():
    if 'email' in session and 'reg_number' in session:
        email = session['email']
        reg_number = session['reg_number']
        department = session['department']
        course = session['course']
        year = session['year']
        login_time = user_data.get(email.split('@')[0], {}).get('login_time', 'Unknown')
        return f'Successfully signed in!<br>Email: {email}<br>Register Number: {reg_number}<br>Department: {department}<br>Course: {course}<br>Year: {year}<br>Login Time: {login_time}'
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
