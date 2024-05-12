from flask import Flask, Response, render_template, redirect, url_for, request, session, jsonify, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import logging
from logging.config import dictConfig
import secrets
import io
import boto3 as boto3
import time 
import pandas as pd
from pandas import json_normalize 
import os 
from dotenv import load_dotenv
import ssl 
import nltk
#import certifi
import requests
from argon2 import PasswordHasher
import datetime
import re
import sqlite3
import urllib.parse
from io import StringIO, BytesIO
import pymysql
import requests
import json
import csv
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg')

from ai.cloud import word_cloud, expenditure_cluster_model

load_dotenv()  # Load environment variables from .env
#from services.basiq_service import BasiqService
from api.temporary_used import optimized_API
from api.temporary_used import API_db_op
from api import database_operation
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

# setup logging configs - needs to be done before flask app is initialised
# can be stored in a dict instead of being passed, but am being memory conservative. python3 also recommends storing in dict over reading from file.
dictConfig(
    { 
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": { 
        "default": {
                "format": "%(levelname)s in %(module)s.py >>> %(message)s",
            },
        "timestamp_file": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s.py >>> %(message)s",
                "datefmt": "%x %X Local",
            },
        },
    "handlers": { 
        "default": { 
            "level": "INFO",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
            },
        "timestamp_stream": {       ##pirnts to console, but with timestamp
            "level": "INFO",
            "formatter": "timestamp_file",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # 
            },
        "dolfin_log": {         # create more module specific loggers here. If adding a new log file, please add to .gitignore
                "class": "logging.FileHandler",
                "filename": "./logs/dolfin.log",    #if log file does not exist, the file will be created. "logs" folder must exist though
                "formatter": "timestamp_file",
            },
        "app_log": {
                "class": "logging.FileHandler",
                "filename": "logs/dolfin-app.log",
                "formatter": "timestamp_file",
            },
        "basiq_log": {
                "class": "logging.FileHandler",
                "filename": "./logs/dolfin-basiq.log",
                "formatter": "timestamp_file",
            },
        "users_log": {
                "class": "logging.FileHandler",
                "filename": "./logs/dolfin-users.log",
                "formatter": "timestamp_file",
            },
    },
    "loggers": { 
        "": {  # root logger? - *should* handle things like flask logs (untested - get reqs still seem come through with info level)
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False
        },
        "dolfin": { 
            "handlers": ["dolfin_log"], #printot console with time stamp, and write to log file
            "level": "INFO",
            "propagate": False
        },
        "dolfin.app" : { 
            "handlers": ["timestamp_stream","app_log"],
            "level": "INFO",
        },
        "dolfin.basiq" : { 
            "handlers": ["timestamp_stream","basiq_log"],
            "level": "INFO",
        },
        "dolfin.users" : { 
            "handlers": ["timestamp_stream","users_log"],
            "level": "INFO",
        },
        } 
    }
)
# "dolfin" logger is essentially a master log. "dolfin.app" is a child logger of the "dolfin" logger. ".app" and ".basiq" are set to automatically propagate back to the master log.
#master_log  = logging.getLogger("dolfin")
app_log     = logging.getLogger("dolfin.app")
#basiq_log   = logging.getLogger("dolfin.basiq")
user_log    = logging.getLogger("dolfin.users")

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

# Setup BASIQ functions
user_ops = API_db_op
db_op = database_operation
API_CORE_ops = optimized_API.Core(os.getenv('API_KEY'))
API_DATA_ops = optimized_API.Data()

class User(db.Model):
    id =        db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(80), unique=True, nullable=False)
    email =     db.Column(db.String(80), unique=True, nullable=False)
    password =  db.Column(db.String(255), nullable=False)

class UserTestMap(db.Model):
    id =        db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid =    db.Column(db.String(80), unique=True, nullable=False)
    testid =    db.Column(db.Integer, nullable=False)

class UserAuditLog(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.datetime.now)
    username =  db.Column(db.String(80), nullable=False)
    action =    db.Column(db.String(80), nullable=False)
    message =   db.Column(db.String(255), nullable=False)

# Our new User database, pending Address fields
class UsersNew(db.Model):
    id =        db.Column(db.Integer, primary_key=True, nullable=False)
    username =  db.Column(db.String(30), unique=True, nullable=False)
    email =     db.Column(db.String(255), nullable=False)
    mobile =    db.Column(db.String(12), nullable=False)
    first_name =    db.Column(db.String(255), nullable=False)
    middle_name =   db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=False)
    password =  db.Column(db.String(255), nullable=False)
    pwd_pt =    db.Column(db.String(255), nullable=True)
    b_id_temp = db.Column(db.String(255), nullable=True)

class UserAddress(db.Model):
    __tablename__ = 'user_address'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    address1 = db.Column(db.String(255), nullable=False)
    address2 = db.Column(db.String(255), nullable=True)
    suburb = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)
    validation = db.Column(db.String(10),nullable=True)

class Response(db.Model):
    __tablename__ = 'surveyresponses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False)
    response1 = db.Column(db.String(10), nullable=False)
    response1_2 = db.Column(db.String(255), nullable=False)
    response2 = db.Column(db.String(30), nullable=False)
    response3 = db.Column(db.String(50), nullable=False)
    response4 = db.Column(db.String(50), nullable=False)
    response4_2 = db.Column(db.String(255), nullable=False)
    response5 = db.Column(db.String(10), nullable=False)
    response5_2 = db.Column(db.String(255), nullable=False)
    response6 = db.Column(db.String(25), nullable=False)
    response7 = db.Column(db.String(255), nullable=False)
    response8 = db.Column(db.String(255), nullable=False)
    response9 = db.Column(db.Integer, nullable=False)
    
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("Error creating database:", str(e))

# do, then print confirmation/error
user_ops.init_dolfin_db()
# Debug and easy testing with API reference
# print(API_CORE_ops.generate_auth_token())

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

# RE-LOG = redo audit log function calls
# transfer user to template
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user_id = session['user_id']
        return dict(user_id=user_id)
    return dict()

# check user_id
@app.before_request
def before_request():
    def check_auth():
        # skip
        if request.path.startswith('/static'):
            return
        if request.path == '/' or request.path == '/login' or request.path == '/register' or request.path == '/submit'or request.path == '/submit':
            return
        # check
        print('@session[user_id]', session.get('user_id'))
        if session.get('user_id') is None:
            app_log.warning("AUTH: No user session active. Redirected to login.") # Should we capture IP?
            return redirect('/login')
    return check_auth()

# make sure no cache
@app.after_request
def add_no_cache_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ROUTING
## LANDING PAGE
@app.route("/",methods = ['GET']) #Initial landing page for application
def landing():
    """ Log testing breaker
    master_log.info("Test - At landing page")
    app_log.info("APP Test - At landing page")
    basiq_log.info("basiq test - At landing page")"""
    return render_template('landing.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':

#         input_username = request.form['username']
#         input_password = request.form['password']

#         # Retrieve the user from the (new) database
#         user = UsersNew.query.filter_by(username=input_username).first()

#         arg_hash = PasswordHasher()
#         # If username is correct, check if the input password (once hashed) matches the hash in the users record.
#         # If both are true, send relevant information to session.
#         if user and arg_hash.verify(user.password, input_password):
#             # Successful login, set a session variable to indicate that the user is logged in
#             session['user_id'] = user.username 
#             session['basiq_id'] = user.b_id_temp
#             session['first_name'] = user.first_name

#             # If successful, check if test user or real user.
#             row = UserTestMap.query.filter_by(userid = input_username).first()
#             testId = 0
#             if row != None:
#                 testId = row.testid
#                 print('######### test id:', testId)

#             # Load transactional data
#             #loadDatabase(testId)            

#             # log successful authentication challenge - consider logging multiple tries?
#             user_log.info("AUTH: User %s has been successfully authenticated. Session active."%(user.username)) # capture IP?

#             ## This section should be done on authentication to avoid empty filling the dash
#             user_ops.clear_transactions()  # Ensure no previous data remains from a previous user etc.
                                    

#             cache = user_ops.request_transactions_df(user.username)     # Get a dataframe of the last 500 transactions
#             #print(cache)                                               # used for testing and debugging
                                               
#             user_ops.cache_transactions(cache)                          # Insert cahce in to database and confirm success

#             # redirect to the dashboard.
#             return redirect('/dash')
        
#         ## Otherwise, fail by default:
#         user_log.warning("AUTH: Login attempt as \"%s\" was rejected. Invalid credentials."%(input_username)) # Log. capture IP? Left as warning for now, could change with justification.
#         return 'Login failed. Please check your credentials, and try again.'

#     return render_template('login.html')  # Create a login form in the HTML template

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_email = request.form['email']
        input_password = request.form['password']

        # Verify the user's email and password
        user_id = db_op.verify_user(input_email, input_password)
        if user_id:
            # Successful login, set session variables
            session['user_id'] = user_id

            db_op.clear_transactions(user_id)
            transacdata = db_op.fetch_transactions_by_user(user_id)

            # Load and cache transactions
            cache = db_op.request_transactions(user_id)
            db_op.cache_transactions(user_id,cache)

            # Redirect to the dashboard
            return redirect('/dash')
        else:
            # Failed login attempt
            user_log.warning("AUTH: Login attempt as \"%s\" was rejected. Invalid credentials." % (input_email))
            return 'Login failed. Please check your credentials, and try again.'

    return render_template('login.html')  # Render the login form


## REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        input_username  = request.form['username']
        input_email     = request.form['email']
        input_password  = request.form['password']
        address1        = request.form['address1']
        address2        = request.form['address2']
        suburb          = request.form['suburb']
        state           = request.form['state']
        postcode        = request.form['postcode']
        
        #if the 'validation' checkbox is present in the form data
        # If present, set validation_checkbox to True; otherwise, set it to False
        validation_checkbox = True if 'validation' in request.form else False

        """ OLD DB FORMAT:
        # Check if the username or email already exists in the database
        existing_user = User.query.filter_by(username=input_username).first()
        existing_email = User.query.filter_by(email=input_email).first()

        # OLD Create a new user and add it to the database
        new_user = User(username=input_username, email=input_email, password=input_password)
        db.session.add(new_user)
        db.session.commit()
        """
        #
        existing_user = UsersNew.query.filter_by(username=input_username).first()
        existing_email = UsersNew.query.filter_by(email=input_email).first()
        print(existing_user)

        # If user exists, they need to retry.
        if existing_user or existing_email:
            user_log.info("REGISTER: (ip?) attempted to register as an existing user.") # keep usernames ambiguous, for now
            return 'Username or email already exists. Please choose a different one.'

        """Setup argon2id hasher with default params. Object Default based on RFC second "recommended option", low memory. 
        5900x+3080LHR   with default params is ___verified___ in ~28.9ms
        i5-1135G7       with default params is ___verified___ in ~55.4ms"""
        arg_hash = PasswordHasher()
        input_password = arg_hash.hash(input_password) #; print(hashed)

        # Create a new user and add it to the users_new database
        # Names are currently hard coded pending name fields in registration
        new_user = UsersNew(username=input_username, email=input_email, mobile="+61450627105",
                            first_name="SAMPLE1",middle_name="test",last_name="USER",password=input_password)
        db.session.add(new_user)
        db.session.commit()


        user_ops.register_basiq_id(new_user.id)      # Create a new entity on our API key, based on the data passed into the user registration form
        
        user_ops.link_bank_account(new_user.id)             # A user will need to link an account to their Basiq entity (that they won't see the entity)
        # Log result
        user_log.info("REGISTER: New user %s, (%s %s) successfully registered and added to database."%(new_user.username,new_user.first_name, new_user.last_name))

        # create a new mapping for a user
        # not relevant in users_new but remains in if need for later database gen
        new_user_id = new_user.id
        new_user_map = UserTestMap(userid = input_username, testid=new_user_id)
        db.session.add(new_user_map)
        db.session.commit()

        # Validate address using AddressFinder API and Create a new user address entry to the database
        user = User.query.filter_by(id=new_user_id).first()
        if user:
            user_id = user.id
            # importing API creds
            AFAPI_KEY=os.getenv("AFAPI_KEY")
            AF_SECRET=os.getenv("AF_SECRET")
            print("userid: ",user_id)
            #combining address fields to single value
            address = address1+', '+address2+', '+suburb+', '+state+', '+postcode
            encoded_address = urllib.parse.quote(address)

            if not validation_checkbox:
                 
                # calling address Validation API
                try:
                    fullurl=f"https://api.addressfinder.io/api/au/address/v2/verification/?key={AFAPI_KEY}&secret={AF_SECRET}&format=json&q={encoded_address}&gnaf=1&paf=1&domain=localhost"
                    response =requests.get(fullurl)
                    print("Full address: ",address)
                    print(response.status_code)
                    # prints the int of the status code. Find more at httpstatusrappers.com :)
                except requests.ConnectionError:
                    print("failed to connect, response code: ", response.status_code)
                
                result = response.json()
                print("result of json req:", result )
                        
                respvalidation=checkAF_response(result)
                if respvalidation:
                    new_user_address = UserAddress(id=user_id, username=input_username, address1=address1, address2=address2, suburb=suburb, state=state, postcode=postcode,validation='Yes')
                    db.session.add(new_user_address)
                    db.session.commit()
                if not respvalidation:
                    message="Invalid Address, please check !"
                    print("rendering register page with error...")
                    #User.query.filter_by(id=new_user_id).delete()
                    #db.session.commit()
                    #UserTestMap.query.filter_by(id=new_user_id).delete()
                    #db.session.commit()
                    return render_template("register.html", msg=message)

            if validation_checkbox:
                new_user_address = UserAddress(id=user_id, username=input_username, address1=address1, address2=address2, suburb=suburb,state=state, postcode=postcode,validation='No')
                db.session.add(new_user_address)
                db.session.commit()

        return redirect('/login')

    return render_template('register.html')  # Create a registration form in the HTML template



def checkAF_response(responsedata):
     # Check if the response contains valid address information
    if responsedata['success']:
        if responsedata['matched']: # Address is valid
            print("Address Validated")
            return True
        else:
            # Address is not valid
            print("invalid address...")
            return False

        return redirect('/login') # unreachbale warning

    return render_template('register.html')  # Create a registration form in the HTML template

## SIGN OUT
@app.route('/signout')
def sign_out():
    if 'user_id' in session:
        user_id = session['user_id']
        #user_ops.clear_transactions()
        db_op.clear_transactions(user_id)
        user_log.info("LOGOUT: %s has logged out." % user_id)
        session.pop('user_id', None)
    return redirect('/')

@app.route('/dash',methods=['GET','POST'])
def auth_dash2(): 
    user_id     = session.get('user_id') # Not used right now.
    first_name  = session.get('first_name')
    if request.method == 'GET':
        transactions_df = db_op.fetch_transactions_by_user(user_id)
        transactions_df['postDate'] = pd.to_datetime(transactions_df['postDate'])
        ## Accout relative code here

        defacc = 'ALL'

        # Select Account 
        dfxx = pd.DataFrame(transactions_df['account'].unique(), columns=['account'])
        dfxx = pd.concat([pd.DataFrame([{'account': 'ALL'}]), dfxx], ignore_index=True)
        jfxx = dfxx.to_json(orient='records')

        # Get class for pie chart
        dfx1 = transactions_df[['class']].dropna().to_json(orient='records')

        # Get subclass for doughnut chart
        dfx2 = transactions_df[['subClass_title']].dropna().to_json(orient='records')

        # Get transaction values for bar chart
        dfx3 = transactions_df[['amount', 'direction']].dropna().to_json(orient='records')

        # Line chart datasets
        dfx4 = transactions_df[['balance', 'postDate']].to_json(orient='records')
        
        dfx5 = df3.to_json(orient='records')

        curr_bal = transactions_df['balance'].iloc[-1] if not transactions_df.empty else 0

        curr_range = transactions_df['balance'].max() - transactions_df['balance'].min() if not transactions_df.empty else 0

        transactions_df['day'] = transactions_df['postDate'].dt.day
        transactions_df['month'] = transactions_df['postDate'].dt.month
        transactions_df['year'] = transactions_df['postDate'].dt.year

        # Create `dfx8` with relevant columns
        dfx8 = transactions_df[['amount', 'class', 'day', 'month', 'year']]
        jfx8 = dfx8.to_json(orient='records')
        
        print(jfx8)

        return render_template("dash2.html",
                               jsd1=dfx1, jsd2=dfx2, jsd3=dfx3,
                               jsd4=dfx4, jsd5=dfx5,
                               jsd6=curr_bal, jsd7=curr_range,
                               jsd8=jfx8, user_id=first_name,
                               jsxx=jfxx, defacc='ALL', show_alert=True)
        
    
    if request.method == "POST":
        # Get the account value from the JSON payload
        data = request.get_json()
        account_value = data.get('account', None)
        print(account_value)

        if account_value == 'ALL':
            
            defacc = account_value
            user_id = session.get('user_id')
            
            # Fetch all transactions using `fetch_transactions_by_user`
            transactions_df = db_op.fetch_transactions_by_user(user_id)
            transactions_df['postDate'] = pd.to_datetime(transactions_df['postDate'])

            # Extract unique accounts
            dfxx = pd.DataFrame(transactions_df['account'].unique(), columns=['account'])
            dfxx = pd.concat([pd.DataFrame([{'account': 'ALL'}]), dfxx], ignore_index=True)
            jfxx = dfxx.to_json(orient='records')

            # Get class for pie chart
            dfx1 = transactions_df[['class']].dropna().to_json(orient='records')

            # Get subclass for doughnut chart
            dfx2 = transactions_df[['subClass_title']].dropna().to_json(orient='records')

            # Get transaction values for bar chart
            dfx3 = transactions_df[['amount', 'direction']].dropna().to_json(orient='records')
            
            # Line chart datasets
            dfx4 = transactions_df[['balance', 'postDate']].to_json(orient='records')
            
            dfx5 = df3.to_json(orient='records')

            curr_bal = transactions_df['balance'].iloc[-1] if not transactions_df.empty else 0
            
            curr_range = transactions_df['balance'].max() - transactions_df['balance'].min() if not transactions_df.empty else 0

            transactions_df['day'] = transactions_df['postDate'].dt.day
            transactions_df['month'] = transactions_df['postDate'].dt.month
            transactions_df['year'] = transactions_df['postDate'].dt.year
            dfx8 = transactions_df[['amount', 'class', 'day', 'month', 'year']]
            jfx8 = dfx8.to_json(orient='records')
            
            updated_data = {
                'currentBalance': curr_bal,
                'balanceRange': curr_range,
                'jsd1': dfx1,
                'jsd2': dfx2,
                'jsd3': dfx3,
                'jsd4': dfx4,
                'jsd5': dfx5,
                'jsd8': jfx8,
                'user_id': first_name,
                'jsxx': jfxx,
                'defacc': defacc,
            }

            return jsonify(updated_data)
            
        if account_value != 'ALL':

            user_id = session.get('user_id')

            defacc = account_value

            transactions_df = db_op.fetch_transactions_by_user(user_id)
            transactions_df['postDate'] = pd.to_datetime(transactions_df['postDate'])

            # Filter transactions for the specified `account_value`
            filtered_df = transactions_df[transactions_df['account'] == account_value]

            # Extract unique accounts and ensure 'ALL' is included
            dfxx = pd.DataFrame(transactions_df['account'].unique(), columns=['account'])
            dfxx = pd.concat([pd.DataFrame([{'account': 'ALL'}]), dfxx], ignore_index=True)
            jfxx = dfxx.to_json(orient='records')

            # Get class for pie chart
            dfx1 = filtered_df[['class']].dropna().to_json(orient='records')

            # Get subclass for doughnut chart
            dfx2 = filtered_df[['subClass_title']].dropna().to_json(orient='records')

            # Get transaction values for bar chart
            dfx3 = filtered_df[['amount', 'direction']].dropna().to_json(orient='records')

            # Line chart datasets
            dfx4 = filtered_df[['balance', 'postDate']].to_json(orient='records')
            
            dfx5 = df3.to_json(orient='records')

            curr_bal = filtered_df['balance'].iloc[-1] if not filtered_df.empty else 0

            curr_range = filtered_df['balance'].max() - filtered_df['balance'].min() if not filtered_df.empty else 0

            filtered_df['day'] = filtered_df['postDate'].dt.day
            filtered_df['month'] = filtered_df['postDate'].dt.month
            filtered_df['year'] = filtered_df['postDate'].dt.year
            dfx8 = filtered_df[['amount', 'class', 'day', 'month', 'year']]
            jfx8 = dfx8.to_json(orient='records')

            updated_data = {
                'currentBalance': curr_bal,
                'balanceRange': curr_range,
                'jsd1': dfx1,
                'jsd2': dfx2,
                'jsd3': dfx3,
                'jsd4': dfx4,
                'jsd5': dfx5,
                'jsd8': jfx8,
                'user_id': first_name,
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

## APPLICATION FINANCIAL WELLBEING SURVEY PAGE 
@app.route('/RFW-prototype/')
def auth_survey(): 
        return render_template("RFW-prototype.html")
    
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
@app.route('/profile')
def profile():
    # Get transaction values for account
    if request.method == 'GET':
        user_id = session.get('user_id')
        email = session.get('email')
        
        # Fetch transactions for the user
        transactions_df = db_op.fetch_transactions_by_user(user_id)
        
        # Convert 'postDate' to datetime if it's not already
        transactions_df['postDate'] = pd.to_datetime(transactions_df['postDate'])
        
        # Account
        dfxx = pd.DataFrame(transactions_df['account'].unique(), columns=['account'])
        new_record = pd.DataFrame([{'account': 'ALL'}])
        dfxx = pd.concat([new_record, dfxx], ignore_index=True)
        jfxx = dfxx.to_json(orient='records')
        
        # Get transaction values for balance indicator
        dfx3 = transactions_df[['amount', 'direction']]
        jfx3 = dfx3.to_json(orient='records')
        curr_bal = transactions_df['balance'].iloc[0] if not transactions_df.empty else 0
        
        # Transactions
        dfx8 = transactions_df[['amount', 'class', 'postDate']].sort_values('postDate', ascending=False).head(5)
        dfx8['day'] = dfx8['postDate'].dt.day
        dfx8['month'] = dfx8['postDate'].dt.month
        dfx8['year'] = dfx8['postDate'].dt.year
        dfx8 = dfx8[['amount', 'class', 'day', 'month', 'year']]
        jsd8 = dfx8.to_dict(orient='records')
        jfx8 = json.dumps(jsd8)
        
        defacc = 'ALL'
        
        return render_template("profile.html", jsd8=jfx8, email=email, jsd6=curr_bal, jsxx=jfxx, jsd3=jfx3, user_id=user_id, defacc=defacc)
def generate_pie_chart(data, category, custom_labels=None):
    # Count the occurrences of each value in the given category
    value_counts = data[category].value_counts()

    # Create a pie chart
    plt.figure(figsize=(7, 5))
    
    
    # Check if custom labels are provided
    labels = custom_labels if custom_labels else value_counts.index
    plt.pie(value_counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=['red', 'orange', 'yellow', 'green', 'blue'])
    plt.title(f'{category} Distribution')

    # Add a legend
    plt.legend(labels, title=f'{category} Legend', loc='center left', bbox_to_anchor=(1, 0.5))

    # Save the chart to a BytesIO object
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight')
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
        chart_data[category] = generate_pie_chart(data, category)

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

    # Generate the pie chart
    chart_data = generate_pie_chart(data, category)

    # Render the chart in an HTML template
    return render_template('chart.html', chart_data=chart_data)

# APPLICATION USER RESET PASSWORD PAGE
@app.route('/resetpw', methods=['GET', 'POST'])
def resetpw():
        return render_template('resetpw.html')

# APPLICATION USER SURVEY
# APPLICATION USER SURVEY
@app.route('/survey',  methods=['GET','POST'])
def survey():
    return render_template("survey.html")

@app.route('/submit', methods=['POST'])
def submit():
    if request.is_json:
        data = request.json
        # Process the received JSON data here
        print(data)
        email="test@mail"
        # email = User.query.filter_by(email=email).first()
        print("user email: ", email)
        question_1_yes = data.get('question_1_yes')
        question_1_no = data.get('question_1_no')
        # Assigning response based on the values of question_1_yes and question_1_no
        if question_1_yes is True:
            response_1 = 'Yes'
        elif question_1_no is True:
            response_1 = 'No'
        else:
            response_1 = 'None'
        
        text_box_1_data = data.get('text_box_1')
        response1_2 = str(text_box_1_data) if 'text_box_1' in data else 'None'
        satisfaction_value=data.get('satisfaction_value')
        response_2=str(satisfaction_value) if 'satisfaction_value' in data else 'None'
        ease_of_access_value=data.get('ease_of_access_value')
        response_3=str(ease_of_access_value) if 'ease_of_access_value' in data else 'None'
          
        question_4_yes = data.get('question_4_yes')
        question_4_no = data.get('question_4_no')

            # Assigning response based on the values of question_1_yes and question_1_no
        if question_4_yes is True:
            response_4 = 'Yes'
        elif question_4_no is True:
            response_4 = 'No'
        else:
            response_4 = 'None'

        text_box_2_data = data.get('text_box_2')
        response4_2 = str(text_box_2_data) if 'text_box_2' in data else 'None'
        question_5_yes = data.get('question_5_yes')
        question_5_no = data.get('question_5_no')
        # Assigning response based on the values of question_5_yes and question_5_no
        if question_5_yes is True:
            response_5 = 'Yes'
        elif question_5_no is True:
            response_5 = 'No'
        else:
            response_5 = 'None'

        text_box_3_data = data.get('text_box_3')
        response5_2 = str(text_box_3_data) if 'text_box_3' in data else 'None'
        frequency_value=data.get('frequency_value')
        response_6=str(frequency_value) if 'frequency_value' in data else 'None'
        additional_features = data.get('additional_features')
        response_7=str(additional_features) if 'additional_features' in data else 'None'
        privacy_security_concerns=data.get('privacy_security_concerns')
        response_8=str(privacy_security_concerns) if 'privacy_security_concerns' in data else 'None'
        feelings_question = data.get('feelings_question')
        response_9=str(feelings_question) if 'feelings_question' in data else 'None'
        print("responses:"+response_1+response1_2+response_2+response_3+response_4+response4_2+response_5+response5_2+response_6+response_7+response_8+response_9)
        response = Response(email=email, response1=response_1,response1_2=response1_2, response2=response_2,response3=response_3,response4=response_4,response4_2=response4_2,
                        response5=response_5,response5_2=response5_2,response6=response_6,response7=response_7,response8=response_8,response9=response_9)
        db.session.add(response)
        db.session.commit()
        message="Thanks for your taking the survey !"
                    
        return render_template("survey.html", msg=message)
    
@app.route('/delete_account/')
def del_acc():
        return render_template("delete_account.html")
 
@app.route('/delete_account', methods=['POST'])
def delete_user_account():
    if 'user_id' in session:
        user_id = session['user_id']
        result = db_op.delete_account(user_id)  # Assuming delete_user_account function is defined in db_op
        session.pop('user_id', None)  # Clear the session after deleting the account
        user_log.info("Account deleted: %s" % user_id)  # Log account deletion
        flash(result)  # Optionally, you can flash a message indicating successful deletion
        return redirect('/')
    else:
        # Handle the case where no user is logged in or session expired
        return redirect('/')


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

global current_trans_data_with_level
@app.route('/dash/epv')
def epv_load():
    global current_trans_data_with_level
    con = sqlite3.connect("transactions_ut.db")
    cursor = con.cursor()
    query = "SELECT * FROM transactions"
    cursor.execute(query)

    data = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    trans_data = pd.DataFrame(data, columns=columns)
    con.close()
    trans_data_with_level, data_cluster = expenditure_cluster_model.cluster(trans_data)
    current_trans_data_with_level = trans_data_with_level
    re = {
        'data_cluster': data_cluster
    }
    return jsonify(re)


@app.route('/dash/epv/generate_word_cloud', methods=['POST'])
def generate_wordcloud():
    data = request.json
    level = data.get('level', 'level 0')
    mode = data.get('mode', 'default')
    response = word_cloud.generate(current_trans_data_with_level, level, mode)
    return response
# Run the Flask appp
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000, debug=True, threaded=False)