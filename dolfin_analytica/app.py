from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect
import secrets
import bcrypt
import os
import time
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        # Access form data using request.form
        username = request.form['username']
        password = request.form['password']

        if username == 'dsuser':
            if password == 'dolfin123':

        # After processing the data, you can redirect to the /loading route
                return redirect(url_for('loading'))

    return render_template('landing.html')

# SQL Database Configure
app.config['SECRET_KEY'] = secrets.token_hex(16) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db/user_database.db')

# SQL Database Configure
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class UserTestMap(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.String(80), unique=True, nullable=False)
    testid = db.Column(db.Integer, nullable=False)

class UserAuditLog(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.datetime.now)
    username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(255), nullable=False)

try:
    with app.app_context():
        db.create_all()
except Exception as e:
     print("Error creating database:", str(e))

#Logging authentication and output to txt file
def add_user_audit_log(username, action, message):
    new_log = UserAuditLog(username=username, action=action, message=message)
    print(new_log)
    db.session.add(new_log)
    db.session.commit() 
    with open("audit.txt", 'a') as file:
        file.write(f"[{new_log.timestamp}] [user-{action}]  username: {username}:  {message}\n")


#LOGIN ROUTE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        input_username = request.form['username']
        input_password = request.form['password']

        # Retrieve the user from the database
        user = User.query.filter_by(username=input_username).first()

        # Check if the user exists and the password is correct with stored hash
        if user and bcrypt.checkpw(input_password.encode('utf-8'), user.password):
            # Successful login, set a session variable to indicate that the user is logged in
            session['user_id'] = user.username 

            # If successful, check if test user or real user.
            row = UserTestMap.query.filter_by(userid = input_username).first()
            testId = 0
            if row != None:
                testId = row.testid
                print('######### test id:', testId)
        
            #Successful login
            add_user_audit_log(input_username, 'login-success', 'User logged in successfully.')
            # redirect to  main.
            return redirect('/main')
        
        ## Otherwise:
        # log un-successful authentication challenge
        add_user_audit_log(input_username, 'login-fail', 'User login failed.')
        return 'Login failed. Please check your credentials.'

    return render_template('login.html')  # Create a login form in the HTML template


@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/main')
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)