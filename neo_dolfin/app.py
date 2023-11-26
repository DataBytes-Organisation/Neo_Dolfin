from flask import Flask, Response, render_template, redirect, url_for, request, session, jsonify
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
#df4 = pd.read_csv('static/data/transaction_ut.csv')

# SQL User Credential Database Configure
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address1 = db.Column(db.String(120), nullable=False)
    address2 = db.Column(db.String(120), nullable=False)
    suburb = db.Column(db.String(80), nullable=False)
    postcode = db.Column(db.Integer, nullable=False)

class UserTestMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(80), unique=True, nullable=False)
    testid = db.Column(db.Integer, nullable=False)

try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("Error creating database:", str(e))

# SQLite User Data Database Setup
#df4.drop(['enrich', 'links'], axis=1, inplace=True) # Drop unnecessary columns
#df4['transactionDate'] = pd.to_datetime(df4['transactionDate'], format='%d/%m/%Y') # Convert 'transactionDate' to datetime format for easy manipulation
#df4['day'] = df4['transactionDate'].dt.day # Create new columns for day, month, and year
#df4['month'] = df4['transactionDate'].dt.month # Create new columns for day, month, and year
#df4['year'] = df4['transactionDate'].dt.year # Create new columns for day, month, and year

# Function to clean the 'subClass' column
#def clean_subClass(row):
#    if pd.isnull(row['subClass']) and row['class'] == 'cash-withdrawal':
#        return 'cash-withdrawal'
#    if row['subClass'] == '{\\title\\":\\"\\"':
#        return 'bank-fee'
#    match = re.search(r'\\title\\":\\"(.*?)\\"', str(row['subClass']))
#    if match:
#        extracted_subClass = match.group(1)
#        if extracted_subClass == 'Unknown':
#            return row['description']
#        return extracted_subClass
#    return row['subClass']

# df4['subClass'] = df4.apply(clean_subClass, axis=1) # Clean the 'subClass' column
# df4['subClass'] = df4['subClass'].apply(lambda x: 'Professional and Other Interest Group Services' if x == '{\\title\\":\\"Civic' else x) # Update specific 'subClass' values
# Check if the SQLite database file already exists
# db_file = "db/transactions_ut.db"
# if not os.path.exists(db_file):
    # If the database file doesn't exist, create a new one
#     conn = sqlite3.connect(db_file)
    # Import the cleaned DataFrame to the SQLite database
#     df4.to_sql("transactions", conn, if_exists="replace", index=False)
#     conn.close()
# else:
    # If the database file already exists, connect to it
#     conn = sqlite3.connect(db_file)

## Basiq API 
basiq_service = BasiqService()

# GEO LOCK MIDDLEWARE - Restricts to Australia or Localhost IPs
class GeoLockChecker(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        ip_addr = environ.get('REMOTE_ADDR', '')
        if self.is_australia_or_localhost(ip_addr):
            # Proceed normally if user in AU or Localhost
            return self.app(environ, start_response)
        else:
            response = Response('Sorry, you are restricted from accessing this content. It is only available in Australia.', mimetype='text/html', status=403)
            return response(environ, start_response)
        
    def is_australia_or_localhost(self, ip_addr):
        if ip_addr == "127.0.0.1":
            return 1
        response = requests.get('http://ip-api.com/json/' + ip_addr)
        if response.status_code == 200:
            geo_info = response.json()
            if(geo_info["country"] == "Australia"):
                return 1
            else:
                return 0
        else:
            return 0


app.wsgi_app = GeoLockChecker(app.wsgi_app)

# ROUTING
## LANDING PAGE
@app.route("/",methods = ['GET','POST']) #Initial landing page for application
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve the user from the database
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            # Successful login, set a session variable to indicate that the user is logged in
            session['user_id'] = user.username 

            # If successful, check if test user or real user.
            row = UserTestMap.query.filter_by(userid = username).first()
            testId = 0
            if row != None:
                 testId = row.testid
                 print('######### test id:', testId)

            # Load transactional data
            loadDatabase(testId)            

            # redirect to the dashboard.
            return redirect('/dash')
        

        return 'Login failed. Please check your credentials.'

    return render_template('login.html')  # Create a login form in the HTML template

## REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address1 = request.form['address1']
        address2 = request.form['address2']
        suburb = request.form['suburb']
        postcode = int(request.form['postcode'])

        # Check if the username or email already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user or existing_email:
            return 'Username or email already exists. Please choose a different one.'

        if postcode < 1000 or postcode > 9999:
            return 'Postcode is invalid. Please enter a valid postcode.'

        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=password, address1=address1, address2=address2, suburb=suburb, postcode=postcode)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')  # Create a registration form in the HTML template

@app.route('/dash',methods=['GET','POST'])
def auth_dash2(): 

    if request.method == 'GET':
        user_id = session.get('user_id')
        con = sqlite3.connect("db/transactions_ut.db")
        cursor = con.cursor() 

        defacc = 'ALL'

        # Select Account 
        cursor.execute('SELECT DISTINCT account FROM transactions')
        query = cursor.fetchall()
        dfxx = pd.DataFrame(query,columns=['account'])
        new_record = pd.DataFrame([{'account': 'ALL'}])
        dfxx = pd.concat([new_record, dfxx], ignore_index=True)
        jfxx = dfxx.to_json(orient='records')

        # Get class for pie chart
        cursor.execute('SELECT class FROM transactions')
        query = cursor.fetchall()
        dfx1 = pd.DataFrame(query,columns=['class'])
        jfx1 = dfx1.to_json(orient='records')

        # Get subclass for doughnut chart
        cursor.execute('SELECT subclass FROM transactions')
        query = cursor.fetchall()
        dfx2 = pd.DataFrame(query,columns=['subclass'])
        jfx2 = dfx2.to_json(orient='records')

        # Get transaction values for bar chart
        cursor.execute('SELECT amount,direction FROM transactions')
        query = cursor.fetchall()
        dfx3 = pd.DataFrame(query,columns=['amount','direction'])
        jfx3 = dfx3.to_json(orient='records')

        # Line chart datasets
        cursor.execute('SELECT balance,postDate FROM transactions')
        query = cursor.fetchall()
        dfx4 = pd.DataFrame(query,columns=['balance','postDate'])
        dfx4 = dfx4.to_json(orient='records')
        
        dfx5 = df3.to_json(orient='records')

        cursor.execute('SELECT balance FROM transactions LIMIT 1')
        query = cursor.fetchone()
        curr_bal = query[0]

        cursor.execute('SELECT MAX(balance) - MIN(balance) AS balance_range FROM transactions')
        query = cursor.fetchone()
        curr_range = query[0]
        print(curr_range)

        cursor.execute('SELECT amount,class,day,month,year FROM transactions LIMIT 1')
        query = cursor.fetchall()
        dfx8= pd.DataFrame(query,columns=['amount','class','day','month','year'])
        jfx8 = dfx8.to_json(orient='records')
        print(jfx8)

        return render_template("dash2.html",jsd1=jfx1, jsd2=jfx2, jsd3=jfx3, jsd4=dfx4, jsd5=dfx5, jsd6=curr_bal, jsd7=curr_range, jsd8=jfx8, user_id=user_id, jsxx=jfxx, defacc=defacc)
        
    if request.method == "POST":
            # Get the account value from the JSON payload
        data = request.get_json()
        account_value = data.get('account', None)
        print(account_value)

        if account_value == 'ALL':
            
            defacc = account_value
            user_id = session.get('user_id')
            con = sqlite3.connect("db/transactions_ut.db")
            cursor = con.cursor() 
            
            cursor.execute('SELECT DISTINCT account FROM transactions')
            query = cursor.fetchall()
            dfxx = pd.DataFrame(query,columns=['account'])
            new_record = pd.DataFrame([{'account': 'ALL'}])
            dfxx = pd.concat([new_record, dfxx], ignore_index=True)
            jfxx = dfxx.to_json(orient='records')

            # Get class for pie chart
            cursor.execute('SELECT class FROM transactions')
            query = cursor.fetchall()
            dfx1 = pd.DataFrame(query,columns=['class'])
            jfx1 = dfx1.to_json(orient='records')

            # Get subclass for doughnut chart
            cursor.execute('SELECT subclass FROM transactions')
            query = cursor.fetchall()
            dfx2 = pd.DataFrame(query,columns=['subclass'])
            jfx2 = dfx2.to_json(orient='records')

            # Get transaction values for bar chart
            cursor.execute('SELECT amount,direction FROM transactions')
            query = cursor.fetchall()
            dfx3 = pd.DataFrame(query,columns=['amount','direction'])
            jfx3 = dfx3.to_json(orient='records')

            # Line chart datasets
            cursor.execute('SELECT balance,postDate FROM transactions')
            query = cursor.fetchall()
            dfx4 = pd.DataFrame(query,columns=['balance','postDate'])
            dfx4 = dfx4.to_json(orient='records')
            
            dfx5 = df3.to_json(orient='records')

            cursor.execute('SELECT balance FROM transactions LIMIT 1')
            query = cursor.fetchone()
            curr_bal = query[0]
            
            cursor.execute('SELECT MAX(balance) - MIN(balance) AS balance_range FROM transactions')
            query = cursor.fetchone()
            curr_range = query[0]

            cursor.execute('SELECT amount,class,day,month,year FROM transactions LIMIT 1')
            query = cursor.fetchall()
            dfx8= pd.DataFrame(query,columns=['amount','class','day','month','year'])
            jfx8 = dfx8.to_json(orient='records')
            
            updated_data = {
                'currentBalance': curr_bal,
                'balanceRange': curr_range,
                'jsd1': jfx1,
                'jsd2': jfx2,
                'jsd3': jfx3,
                'jsd4': dfx4,
                'jsd5': dfx5,
                'jsd8': jfx8,
                'user_id': user_id,
                'jsxx': jfxx,
                'defacc': defacc,
            }

            return jsonify(updated_data)
            
        if account_value != 'ALL':

            user_id = session.get('user_id')
            con = sqlite3.connect("db/transactions_ut.db")
            cursor = con.cursor() 

            defacc = account_value

            cursor.execute('SELECT DISTINCT account FROM transactions')
            query = cursor.fetchall()
            dfxx = pd.DataFrame(query,columns=['account'])
            new_record = pd.DataFrame([{'account': 'ALL'}])
            dfxx = pd.concat([new_record, dfxx], ignore_index=True)
            jfxx = dfxx.to_json(orient='records')

            # Get class for pie chart
            cursor.execute('SELECT class FROM transactions WHERE account = ?', (account_value,))
            query = cursor.fetchall()
            dfx1 = pd.DataFrame(query,columns=['class'])
            jfx1 = dfx1.to_json(orient='records')

            # Get subclass for doughnut chart
            cursor.execute('SELECT subclass FROM transactions WHERE account = ?', (account_value,))
            query = cursor.fetchall()
            dfx2 = pd.DataFrame(query,columns=['subclass'])
            jfx2 = dfx2.to_json(orient='records')

            # Get transaction values for bar chart
            cursor.execute('SELECT amount,direction FROM transactions WHERE account = ?', (account_value,))
            query = cursor.fetchall()
            dfx3 = pd.DataFrame(query,columns=['amount','direction'])
            jfx3 = dfx3.to_json(orient='records')

            # Line chart datasets
            cursor.execute('SELECT balance,postDate FROM transactions WHERE account = ?', (account_value,))
            query = cursor.fetchall()
            dfx4 = pd.DataFrame(query,columns=['balance','postDate'])
            dfx4 = dfx4.to_json(orient='records')
            
            dfx5 = df3.to_json(orient='records')

            cursor.execute('SELECT balance FROM transactions WHERE account = ? LIMIT 1', (account_value,))
            query = cursor.fetchone()
            curr_bal = query[0]

            cursor.execute('SELECT MAX(balance) - MIN(balance) AS balance_range FROM transactions WHERE account = ?', (account_value,))
            query = cursor.fetchone()
            curr_range = query[0]

            cursor.execute('SELECT amount,class,day,month,year FROM transactions WHERE account = ? LIMIT 1', (account_value,))
            query = cursor.fetchall()
            dfx8= pd.DataFrame(query,columns=['amount','class','day','month','year'])
            jfx8 = dfx8.to_json(orient='records')

            updated_data = {
                'currentBalance': curr_bal,
                'balanceRange': curr_range,
                'jsd1': jfx1,
                'jsd2': jfx2,
                'jsd3': jfx3,
                'jsd4': dfx4,
                'jsd5': dfx5,
                'jsd8': jfx8,
                'user_id': user_id,
                'jsxx': jfxx,
                'defacc': defacc,
            }

            return jsonify(updated_data)   

@app.route("/load", methods=['GET', 'POST'])
def dashboardLoader():
    return render_template("loadingPage.html")

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
@app.route('/profile')
def profile():
        return render_template("profile.html") 
    
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
    app.run(host='0.0.0.0',port=8000, debug=True, threaded=False)
