from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
import secrets
import boto3 as boto3
import pandas as pd
import logging
import time 
import os 
from dotenv import load_dotenv
import hashlib
import hmac
import base64
import qrcode
#import dash
#import dash_core_components as dcc
#import dash_html_components as html

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
df = pd.read_csv('static/dummies.csv')
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Replace with a secure random key

# AWS STUFF
AWS_REGION = os.environ.get('AWS_REGION')
AWS_COGNITO_USER_POOL_ID = os.environ.get('AWS_COGNITO_USER_POOL_ID')
AWS_COGNITO_APP_CLIENT_ID = os.environ.get('AWS_COGNITO_APP_CLIENT_ID')
AWS_COGNITO_CLIENT_SECRET = os.environ.get('AWS_COGNITO_CLIENT_SECRET')
client = boto3.client('cognito-idp', region_name=AWS_REGION)

# DASH APP
# Initialize Dash app
#dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')  # Set the route to '/dash/'

# TODO: UPDATE DASH APP WITH USER DATA
# Define the Dash layout
#dash_app.layout = dash_layout#

#FUNCTIONS
def is_token_valid():
    access_token = session.get('access_token')
    expiration_timestamp = session.get('token_expiration')

    if not access_token or not expiration_timestamp:
        return False

    current_timestamp = int(time.time())
    if current_timestamp >= expiration_timestamp:
        # Token has expired
        return False

    # Token is still valid
    return True
 
def calculate_secret_hash(client_id, client_secret, username):
    message = username + client_id
    dig = hmac.new(str(client_secret).encode('utf-8'),
                   msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()



#CLASSES
class SignInForm(FlaskForm):
    username = StringField('E-Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SignUpForm(FlaskForm):
    given_name = StringField('Given_name',validators=[DataRequired()])#
    family_name = StringField('Family_name',validators=[DataRequired()])
    nickname = StringField('Nickname',validators=[DataRequired()])
    username = StringField('E-Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class SignUpConfForm(FlaskForm):
    signupconf = PasswordField('Confirmation Code', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class SignUpMFADForm(FlaskForm):
    signupmfadevicename = StringField('MFA Device Name', validators=[DataRequired()])
    signupmfadevicecode = StringField('MFA Device Code', validators=[DataRequired()])
    submit = SubmitField('Sign Up')



# ROUTING
@app.route("/")
def landing():
    return render_template('landing.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        try:
            SecretHash=calculate_secret_hash(AWS_COGNITO_APP_CLIENT_ID, AWS_COGNITO_CLIENT_SECRET, form.username.data)
            # Set session username 
            session['username'] = form.username.data
            response = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': form.username.data,
                    'PASSWORD': form.password.data,
                    'SECRET_HASH': SecretHash
                    },
                ClientId=AWS_COGNITO_APP_CLIENT_ID)
            #print(response)      d
            if response['ChallengeName'] == 'MFA_SETUP': #User has to setup MFA to log in
                response=client.associate_software_token(Session=response['Session'])
                session['username'] = form.username.data
                session['sicode'] = response['SecretCode']
                session['siresponse'] = response['Session']
                print('Moving to Signup MFA Device')
                return redirect('/signupmfad')
            else:      
                # Extract the JWT token and its expiration time from the response
                access_token = response['AuthenticationResult']['AccessToken']
                expires_in = response['AuthenticationResult']['ExpiresIn']

                # Calculate the absolute expiration timestamp for the token
                expiration_timestamp = int(time.time()) + expires_in

                # Store the token and its expiration timestamp in the session
                session['access_token'] = access_token
                session['token_expiration'] = expiration_timestamp
                session['username'] = form.username.data
                print(session['access_token'])
                print(session['username'])
                print(response['ChallengeName'])
                return redirect('/home/')
        except client.exceptions.UserNotConfirmedException:
            # Handle case where the user has not confirmed their email account
            return redirect('/signupconf') #error='User requires confirmation. Check your email address for a verification code.')
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-in error: {e}")
            print(response['ChallengeName'])
            # Handle authentication failure
            return render_template('signin.html', form=form, error='Invalid credentials. Please try again.')

    return render_template('signin.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            response = client.sign_up(
                ClientId=AWS_COGNITO_APP_CLIENT_ID,
                Username=form.username.data,
                Password=form.password.data,
                UserAttributes = [
                    {
                    'Name': 'given_name',
                    'Value': form.given_name.data
                    },
                    {
                    'Name': 'family_name',
                    'Value': form.family_name.data
                    },
                    {
                    'Name': 'nickname',
                    'Value': form.nickname.data
                    }
                ],
                SecretHash=calculate_secret_hash(AWS_COGNITO_APP_CLIENT_ID, AWS_COGNITO_CLIENT_SECRET, form.username.data)
                )
            # If sign-up is successful, redirect to a different page (e.g., a success page or the sign-in page).
            print("Sign-up response:", response)
            return redirect('/signin')
        except client.exceptions.UsernameExistsException:
            # Handle case where the username already exists
            return render_template('signup.html', form=form, error='Username already exists. Please choose a different one.')
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-up error: {e}")
            # Handle other sign-up errors
            return render_template('signup.html', form=form, error='An error occurred. Please try again.')

    return render_template('signup.html', form=form)

@app.route('/signupconf', methods=['GET', 'POST'])
def signupconf():
    form = SignUpConfForm()
    if form.validate_on_submit():
        try:
            response = client.confirm_sign_up(
                ClientId=AWS_COGNITO_APP_CLIENT_ID,
                SecretHash=calculate_secret_hash(AWS_COGNITO_APP_CLIENT_ID, AWS_COGNITO_CLIENT_SECRET, session.get('username')),
                Username=session.get('username'),
                ConfirmationCode=form.signupconf.data
                )
            # If sign-up is successful, redirect to a different page (e.g., a success page or the sign-in page).
            print("Sign-up conf response:", response)
            return redirect('/signin')
        except client.exceptions.ExpiredCodeException:
            # Handle case where the code has expired
            return render_template('signupconf.html', form=form, error='Code has expired, please generate a new one')
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-up error: {e}")
            # Handle other sign-up errors
            return render_template('signupconf.html', form=form, error='An error occurred. Please try again.')
    return render_template('signupconf.html', form=form)

@app.route('/signupconf/resendconfemail', methods=['GET', 'POST'])
def resendconfemail():
    form = SignUpConfForm()
    try:
        response = client.resend_confirmation_code(
            ClientId=AWS_COGNITO_APP_CLIENT_ID,
                SecretHash=calculate_secret_hash(AWS_COGNITO_APP_CLIENT_ID, AWS_COGNITO_CLIENT_SECRET, session.get('username')),
                Username=session.get('username'))
        return render_template('signupconf.html', form=form)
    except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-up error: {e}")
            # Handle other sign-up errors
            return render_template('signupconf.html', form=form, error='An error occurred. Please try again.')
    
@app.route('/signupmfad', methods=['GET', 'POST'])
def signupmfadevice():
    form = SignUpMFADForm()
    awssession=session.get('sisession')
    username=session.get('username')
    awssecretcode=session.get('sicode')

    try:
        qr_img = qrcode.make(
            f"otpauth://totp/{username}?secret={awssecretcode}")
        qr_img.save("static/images/qr.png")
    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"Failed to generate QR code: {e}")
    
    if form.validate_on_submit():
        try:
            response = client.verify_software_token(
                AccessToken=awssession,
                Session=awssession,
                UserCode=form.signupmfadevicecode.data,
                FriendlyDeviceName=form.signupmfadevicename.data)

            print(response)
            #return response

            response = client.respond_to_auth_challenge(
                ClientId=AWS_COGNITO_APP_CLIENT_ID,
                ChallengeName="MFA_SETUP",
                Session=response['Session'],

                SecretHash=calculate_secret_hash(AWS_COGNITO_APP_CLIENT_ID, AWS_COGNITO_CLIENT_SECRET, session.get('username')),
                Username=session.get('username'))
            return render_template('signin.html', form=form, error='MFA Device Subscribed')
        except Exception as e:
                # Log the error for debugging purposes
                logging.error(f"MFA Device Sign-up error: {e}")
                # Handle other sign-up errors
                return render_template('signupmfad.html', form=form, error='Invalid MFA Device ID. Please try again.')
    return render_template('signupmfad.html', form=form, error='Invalid MFA Device ID. Please try again.')

        
    

# Define a Flask route for the Dash app's page
#@app.route('/dash/')
#def dash_page():
#    return dash_app.index()

@app.route('/home/')
def auth_home(): 
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("home.html")
    
@app.route('/news/')
def auth_news(): 
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("news.html")
    
# Run the Flask app
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
