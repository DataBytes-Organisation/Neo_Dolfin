from flask import Flask, Response, render_template, redirect, url_for, request, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import secrets
import io
import boto3 as boto3
import time 
import pandas as pd 
import os 
from dotenv import load_dotenv
import ssl 
import nltk
#import certifi
import datetime
import re
import sqlite3
from services.basiq_service import BasiqService
from io import StringIO
import pymysql
import requests
import json
import csv
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')

load_dotenv()  # Load environment variables from .env
from classes import *
from functions import * 
from services.basiq_service import BasiqService
from ai.chatbot import chatbot_logic

# Access environment variables
PASSWORD = os.getenv("PASSWORD")
PUBLIC_IP = os.getenv("PUBLIC_IP_ADDRESS")
DBNAME = os.getenv("DBNAME")
PROJECT_ID = os.getenv("PROJECT_ID")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

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

with app.app_context():
     db.create_all()

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
#app.wsgi_app = GeoLockChecker(app.wsgi_app)

# ROUTING
## LANDING PAGE
@app.route("/",methods = ['GET']) #Initial landing page for application
def landing():
    return render_template('landing.html')

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

        new_user_id = new_user.id

        new_user_map = UserTestMap(userid = username, testid=new_user_id)
        db.session.add(new_user_map)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')  # Create a registration form in the HTML template

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

        return render_template("dash2.html",jsd1=jfx1, jsd2=jfx2, jsd3=jfx3, jsd4=dfx4, jsd5=dfx5, jsd6=curr_bal, jsd7=curr_range, jsd8=jfx8, user_id=user_id, jsxx=jfxx, defacc=defacc, current_page='dash') # current_page='dash' return variable used for NAVBAR. DO NOT DELETE
        
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
        return render_template("news.html", current_page='news') # current_page='news' USed for Navbar. DO NOT DELETE   

## APPLICATION FAQ PAGE 
@app.route('/FAQ/')
def auth_FAQ(): 
        return render_template("FAQ.html", current_page="FAQ") #  current_page="FAQ" Used for Navbar. DO NOT DELETE
    
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


# Add this route to your Flask app
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Get form data
        features_rating = request.form['features']
        security_rating = request.form['security']
        recommend_rating = request.form['recommend']
        features_valuable = request.form['features_valuable']
        competitors_do_well = request.form['competitors_do_well']
        similarities = request.form['similarities']

        # Create a dictionary with the form data
        feedback_data = {
            'Features Rating': features_rating,
            'Security Rating': security_rating,
            'Recommendation Rating': recommend_rating,
            'Valuable Features': features_valuable,
            'Competitors Do Well': competitors_do_well,
            'Similarities': similarities,
        }

        print("Received Feedback Data:", feedback_data)

        # Log the data to a CSV file
        data_folder = 'data'
        os.makedirs(data_folder, exist_ok=True)

        # Log the data to a CSV file inside the 'data' folder
        csv_filename = os.path.join(data_folder, 'feedback_data.csv')
        file_exists = os.path.isfile(csv_filename)

        with open(csv_filename, mode='a', newline='') as csvfile:
            fieldnames = list(feedback_data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(feedback_data)

        print("Feedback Data Logged to CSV")

        return render_template('feedback_thank_you.html')

    # Render the feedback form if the request is not POST
    return render_template('feedback.html')
    

# APPLICATION USER SPECIFIC  PROFILE PAGE
@app.route('/profile', methods=['GET'])
def profile():
     # Get transaction values for account
      if request.method == 'GET':
        user_id = session.get('user_id')
        con = sqlite3.connect("db/transactions_ut.db")
        cursor = con.cursor() 
        defacc = 'ALL'  
        email = session.get('email') 

        # Account 
        cursor.execute('SELECT DISTINCT account FROM transactions')
        query = cursor.fetchall()
        dfxx = pd.DataFrame(query,columns=['account'])
        new_record = pd.DataFrame([{'account': 'ALL'}])
        dfxx = pd.concat([new_record, dfxx], ignore_index=True)
        jfxx = dfxx.to_json(orient='records')

        # Get transaction values for balance indicator
        cursor.execute('SELECT amount,direction FROM transactions')
        query = cursor.fetchall()
        dfx3 = pd.DataFrame(query,columns=['amount','direction'])
        jfx3 = dfx3.to_json(orient='records')   

        cursor.execute('SELECT balance FROM transactions LIMIT 1')
        query = cursor.fetchone()
        curr_bal = query[0]

        #Transactions 
        cursor.execute('SELECT amount, class, day, month, year FROM transactions ORDER BY postDate DESC LIMIT 5')  
        query = cursor.fetchall()
        dfx8 = pd.DataFrame(query, columns=['amount', 'class', 'day', 'month', 'year'])
        jsd8 = dfx8.to_dict(orient='records')  # Convert DataFrame to list of dictionaries
        jfx8 = json.dumps(jsd8)  # Convert the list of dictionaries to a JSON string
        return render_template("profile.html", jsd8=jfx8, email=email, jsd6=curr_bal, jsxx=jfxx, jsd3=jfx3, user_id=user_id, defacc=defacc)

def generate_bar_chart(category, values):
    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(category, values, color='blue')
    plt.xlabel(category)
    plt.ylabel('Count')
    plt.title(f'{category} Distribution')

    # Save the chart to a BytesIO object
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Encode the image to base64
    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    # Return the encoded image
    return image_base64

@app.route('/visualizations', methods=['GET'])
def visualizations():
    # Assuming 'feedback_data.csv' is your CSV file inside the 'data' folder
    csv_filename = 'data/feedback_data.csv'

    # Read the CSV file into a Pandas DataFrame
    data = pd.read_csv(csv_filename)

    # Get unique categories from the DataFrame columns (excluding non-numeric ones)
    categories = [col for col in data.columns if data[col].dtype == 'int64']

    # Generate the chart data for each category
    chart_data = {}
    for category in categories:
        values = data[category].tolist()
        chart_data[category] = generate_bar_chart(category, values)

    return render_template('visualizations.html', chart_data=chart_data)

@app.route('/visualizations/<category>', methods=['GET'])
def visualize_category(category):
    # Assuming 'feedback_data.csv' is your CSV file
    csv_filename = 'data/feedback_data.csv'

    # Read the CSV file into a Pandas DataFrame
    data = pd.read_csv(csv_filename)

    # Ensure the selected category is a valid column in the DataFrame
    if category not in data.columns or data[category].dtype != 'int64':
        return 'Invalid category or non-numeric data'

    # Get values for the selected category
    values = data[category].tolist()

    # Generate the bar chart
    chart_data = generate_bar_chart(category, values)

    # Render the chart in an HTML template
    return render_template('chart.html', chart_data=chart_data)



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

# Run the Flask appp
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000, debug=True, threaded=False)