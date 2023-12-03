from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import secrets
import boto3 as boto3
import pandas as pd
import time 
import os 
from dotenv import load_dotenv
import logging
import ssl 
import nltk
#import certifi
import requests
import datetime
import re
import sqlite3
import plotly.graph_objects as go
from services.basiq_service import BasiqService
from io import StringIO

load_dotenv()  # Load environment variables from .env
from classes import *
from functions import * 
from services.basiq_service import BasiqService
from ai.chatbot import chatbot_logic

# Chatbot Logic req files for VENV
script_dir = os.path.dirname(os.path.abspath(__file__))
venv_dir = os.path.join(script_dir, 'venv')  # Assumes venv is at the parent directory
nltk_data_path = os.path.join(venv_dir, 'nltk_data')

# Configure SSL for older versions of Python (if needed)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK data into the custom directory
nltk.data.path.append(nltk_data_path)
nltk.download('punkt', download_dir=nltk_data_path)
nltk.download('wordnet', download_dir=nltk_data_path)

app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Replace with a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db/user_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Dataframes
df1 = pd.read_csv('static/data/transaction_ut.csv')
df2 = pd.read_csv('static/data/modified_transactions_data.csv')
df3 = pd.read_csv('static/data/Predicted_Balances.csv')
df4 = pd.read_csv('static/data/transaction_ut.csv')

# SQL User Credential Database Configure
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("Error creating database:", str(e))

# SQLite User Data Database Setup
df4.drop(['enrich', 'links'], axis=1, inplace=True) # Drop unnecessary columns
df4['transactionDate'] = pd.to_datetime(df4['transactionDate'], format='%d/%m/%Y') # Convert 'transactionDate' to datetime format for easy manipulation
df4['day'] = df4['transactionDate'].dt.day # Create new columns for day, month, and year
df4['month'] = df4['transactionDate'].dt.month # Create new columns for day, month, and year
df4['year'] = df4['transactionDate'].dt.year # Create new columns for day, month, and year

# Function to clean the 'subClass' column
def clean_subClass(row):
    if pd.isnull(row['subClass']) and row['class'] == 'cash-withdrawal':
        return 'cash-withdrawal'
    if row['subClass'] == '{\\title\\":\\"\\"':
        return 'bank-fee'
    match = re.search(r'\\title\\":\\"(.*?)\\"', str(row['subClass']))
    if match:
        extracted_subClass = match.group(1)
        if extracted_subClass == 'Unknown':
            return row['description']
        return extracted_subClass
    return row['subClass']

df4['subClass'] = df4.apply(clean_subClass, axis=1) # Clean the 'subClass' column
df4['subClass'] = df4['subClass'].apply(lambda x: 'Professional and Other Interest Group Services' if x == '{\\title\\":\\"Civic' else x) # Update specific 'subClass' values
conn = sqlite3.connect("transactions_ut.db") # Create a new SQLite database in memory and import the cleaned DataFrame
df4.to_sql("transactions", conn, if_exists="replace", index=False)

## Basiq API 
basiq_service = BasiqService()

# ROUTING

## LANDING PAGE
@app.route("/",methods = ['GET','POST']) #Initial landing page for application
def landing():
    return render_template('landing.html')

## LOGIN
from flask import session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve the user from the database
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            # Successful login, set a session variable to indicate that the user is logged in
            session['user_id'] = user.id
            return redirect('/home/')

        return 'Login failed. Please check your credentials.'

    return render_template('login.html')  # Create a login form in the HTML template

## REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user or existing_email:
            return 'Username or email already exists. Please choose a different one.'

        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')  # Create a registration form in the HTML template

@app.route('/home/')
def auth_dash(): 
        return render_template("dash.html")

## APPLICATION NEWS PAGE   
@app.route('/news/')
def auth_news():
        return render_template("news.html")   

## APPLICATION FAQ PAGE 
@app.route('/FAQ/')
def auth_FAQ(): 
        return render_template("FAQ.html")
    
# APPLICATION TERMS OF USE PAGE 
@app.route('/terms-of-use/')
def open_terms_of_use():
        return render_template("TermsofUse.html") 
    
# APPLICATION TERMS OF USE-AI PAGE 
@app.route('/terms-of-use-ai/')
def open_terms_of_use_AI():
        return render_template("TermsofUse-AI.html") 
    
# APPLICATION Article Template PAGE 
@app.route('/articleTemplate/')
def open_article_template():
        return render_template("articleTemplate.html") 
    
# APPLICATION USER SPECIFIC  PROFILE PAGE
@app.route('/profile', methods=['GET', 'POST'])
def profile():
<<<<<<< Updated upstream

    #request userid/username of current logged in user
    if request.method =='GET':
        user_id = session.get('user_id')

    #specify the database path otherwise it tries to create a new/empty database
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db/user_database.db')
    #connect to the database 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #query to db based on username of current logged in user 
=======
    if request.method =='GET':
        user_id = session.get('user_id')

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db/user_database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
>>>>>>> Stashed changes
    cursor.execute("SELECT email FROM user WHERE username = ?", (session['user_id'],))
    email = cursor.fetchall()
    cursor.execute("SELECT username FROM user WHERE username = ?", (session['user_id'],))
    username = cursor.fetchall()
    conn.close()

<<<<<<< Updated upstream
    #clean the fetched results to remove additional symbols and display as plain text 
=======
>>>>>>> Stashed changes
    email_tuple = email
    username_tuple = username

    email_address = email_tuple[0][0]
    username_symbol = username_tuple[0][0]

    email = email_address.replace("[('", "").replace("',)]", "")
    username = username_symbol.replace("[('", "").replace("',)]", "")

<<<<<<< Updated upstream
    return render_template("profile.html", email=email, username=username, user_id=user_id) 
=======
    return render_template("profile.html", email=email, username=username, user_id=user_id)
>>>>>>> Stashed changes
    
# APPLICATION USER RESET PASSWORD PAGE
@app.route('/resetpw', methods=['GET', 'POST'])
def resetpw():
        return render_template('resetpw.html')

## CHATBOT PAGE 
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'GET':
        return render_template('chatbot.html')
    elif request.method == 'POST':
        user_input = request.get_json().get("message")
        prediction = chatbot_logic.predict_class(user_input)
        sentiment = chatbot_logic.process_sentiment(user_input)
        response = chatbot_logic.get_response(prediction, chatbot_logic.intents, user_input)
        message={"answer" :response}
        return jsonify(message)
    return render_template('chatbot.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000, debug=True)
