from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp
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
import logging 

#import dash
#import dash_core_components as dcc
#import dash_html_components as html

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Replace with a secure random key
app.static_folder = 'static'
df = pd.read_csv('static/dummies.csv')

# AWS STUFF
AWS_REGION = os.environ.get('AWS_REGION')
AWS_COGNITO_USER_POOL_ID = os.environ.get('AWS_COGNITO_USER_POOL_ID')
AWS_COGNITO_APP_CLIENT_ID = os.environ.get('AWS_COGNITO_APP_CLIENT_ID')#
AWS_COGNITO_CLIENT_SECRET = os.environ.get('AWS_COGNITO_CLIENT_SECRET')

client = boto3.client('cognito-idp', region_name=AWS_REGION)

# DASH APP
# Initialize Dash app
#dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')  # Set the route to '/dash/'
#
# TODO: UPDATE DASH APP WITH USER DATA
# Define the Dash layout
#dash_app.layout = dash_layout#

#FUNCTIONS
def is_token_valid(): #Confirm whether access token exists and has not expired, token provided by AWS Cognito, stored in local session
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
 
def calculate_secret_hash(client_id, client_secret, username): #Calculate secret hash, as per AWS API AWS>Documentation>Amazon Cognito?Developer Guide
    message = username + client_id
    dig = hmac.new(str(client_secret).encode('utf-8'),
                   msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()


#CLASSES
class SignInForm(FlaskForm): #Used on signin.html
    username = StringField('E-Mail', validators=[DataRequired(), Email(message="This field requires a valid email address")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SignInMFAForm(FlaskForm): #Used on signinmfa.html
    otp = PasswordField('One Time Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SignUpForm(FlaskForm): #Used on signup.html
    given_name = StringField('Given_name',validators=[DataRequired()])
    family_name = StringField('Family_name',validators=[DataRequired()])
    nickname = StringField('Nickname',validators=[DataRequired()])
    username = StringField('E-Mail', validators=[DataRequired(),  Email(message="This field requires a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(), Regexp("(?=[A-Za-z0-9@#$%^&+!=]+$)^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%^&+!=])(?=.{8,}).*$",
                                                                            message="At least 8 characters, Minimum 1 Uppercase, 1 Lowercase, 1 Number, 1 Special Character and only contains symbols from the alphabet")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class SignUpConfForm(FlaskForm): #Used on signup.html
    signupconf = PasswordField('Confirmation Code', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SignUpMFADForm(FlaskForm): #Used on signupmfad.html
    signupmfadevicename = StringField('MFA Device Name', validators=[DataRequired()])
    signupmfadevicecode = StringField('MFA Device Code', validators=[DataRequired()])
    submit = SubmitField('Register Device')


# ROUTING

# LANDING PAGE
@app.route("/") #Initial landing page for application
def landing():
    return render_template('landing.html')

# SIGN IN PAGE
@app.route('/signin', methods=['GET', 'POST']) #Initial sign in page
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        try:
            # Initiate sign in process
            response = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': form.username.data,
                    'PASSWORD': form.password.data,
                    'SECRET_HASH': calculate_secret_hash(AWS_COGNITO_APP_CLIENT_ID, AWS_COGNITO_CLIENT_SECRET, form.username.data)},
                ClientId=AWS_COGNITO_APP_CLIENT_ID)
            # Log the response for debugging
            print(response)
            logging.debug(f"Initiate Auth Response: {response}") 
            # If user has a registered authentication device lead them to page to enter code
            if response['ChallengeName'] == 'SOFTWARE_TOKEN_MFA': #User has to log in with MFA
                session['siresponse'] = response['Session']
                session['username'] = form.username.data
                return redirect('/signinmfa') #Send to enter MFA OTP
            
            # If user has not registered a MFA device / autheticator lead them to page to do so
            elif response['ChallengeName'] == 'MFA_SETUP': #User has to setup MFA device to log in
                response=client.associate_software_token(Session=response['Session'])
                session['username'] = form.username.data
                session['sicode'] = response['SecretCode']
                session['siresponse'] = response['Session']
                return redirect('/signupmfad') #Send to register MFA device
            
            # If Cognito pool does not use MFA then allow user to sign in
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
                logging.info(f"User {form.username.data} signed in successfully.")
                return redirect('/home/')

        # If user has not confirmed their email they must do so    
        except client.exceptions.UserNotConfirmedException:
            # Handle case where the user has not confirmed their email account
            logging.warning(f"User {form.username.data} attempted to sign in, but email is not confirmed.")
            return redirect('/signupconf')
        
        # General error handling catch for remaining exceptions from sign-in initiation
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-in error: {e}")
            # Handle authentication failure
            return render_template('signin.html', form=form, error='Invalid credentials. Please try again.')

    return render_template('signin.html', form=form)

# SIGN IN USING MFA PAGE
@app.route('/signinmfa', methods=['GET', 'POST']) # Sign in using MFA one time password
def signinmfa():
    form=SignInMFAForm()
    if form.validate_on_submit():
        try:
            response=client.respond_to_auth_challenge(
                ClientId=AWS_COGNITO_APP_CLIENT_ID,
                ChallengeName='SOFTWARE_TOKEN_MFA',
                Session=session.get('siresponse'),
                ChallengeResponses={
                    'USERNAME': session.get('username'),
                    'SECRET_HASH': calculate_secret_hash(AWS_COGNITO_APP_CLIENT_ID, AWS_COGNITO_CLIENT_SECRET, session.get('username')),
                    'SOFTWARE_TOKEN_MFA_CODE':form.otp.data
                    }
            )
            
            # Extract the JWT token and its expiration time from the response
            access_token = response['AuthenticationResult']['AccessToken']
            expires_in = response['AuthenticationResult']['ExpiresIn']

            # Calculate the absolute expiration timestamp for the token
            expiration_timestamp = int(time.time()) + expires_in

            # Store the token and its expiration timestamp in the session
            session['access_token'] = access_token
            session['token_expiration'] = expiration_timestamp
            return redirect('/home/')

        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-in with MFA error: {e}")
            # Handle other sign-up errors
            return render_template('signinmfa.html', form=form, error=e)
    return render_template('signinmfa.html', form=form)

# USER SIGN UP PAGE
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
            session['username'] = form.username.data
            return redirect('/signupconf')
        
        except client.exceptions.UsernameExistsException:
            # Handle case where the username already exists
            return render_template('signup.html', form=form, error='Username already exists. Please choose a different one.')
        
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-up error: {e}")
            # Handle other sign-up errors
            return render_template('signup.html', form=form, error='An error occurred. Please try again.')

    return render_template('signup.html', form=form)

# SIGN-UP EMAIL CONFIRMATION PAGE
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
            return redirect('/signin')
        except client.exceptions.ExpiredCodeException:
            # Handle case where the sign up code has expired
            return render_template('signupconf.html', form=form, error='Code has expired, please generate a new one')
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-up error: {e}")
            # Handle other sign-up errors
            return render_template('signupconf.html', form=form, error='An error occurred. Please try again.')
    return render_template('signupconf.html', form=form)

# ROUTE TO INTITIATE SIGN-UP EMAIL CONFIRMATION BEING SENT AGAIN
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
            logging.error(f"Sign-up Resend Confirmation Email error: {e}")
            # Handle other sign-up errors
            return render_template('signupconf.html', form=form, error='An error occurred. Please try again.')

# REGISTER USER AUTHENTICATION DEVICE PAGE    
@app.route('/signupmfad', methods=['GET', 'POST'])
def signupmfadevice():
    form = SignUpMFADForm()
    awssession=session.get('siresponse')
    username=session.get('username')
    awssecretcode=session.get('sicode')

    #Generate user specific QR code
    qr_img = qrcode.make(
        f"otpauth://totp/{username}?secret={awssecretcode}&issuer=DolFin")
    qr_img.save("static/img/qr.png")
    if form.validate_on_submit():
        try:
            response = client.verify_software_token(
                Session=awssession,
                UserCode=form.signupmfadevicecode.data,
                FriendlyDeviceName=form.signupmfadevicename.data)
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"MFA Device Sign-up error: {e}")
            # Handle other sign-up errors
            return render_template('signupmfad.html', form=form, error='There was an error registering your device. Please try again.')
    return render_template('/home/.html', form=form)

# APPLICATION HOME PAGE - REQUIRES USER TO BE SIGNED IN TO ACCESS
@app.route('/home/')
def auth_home(): 
    if not is_token_valid():
        # INSERT BOTO3 REQUEST HERE
        # CHECK IF USERNAME.FOLDER EXISTS 
            # IF NOT, MAKE A DIRECTORY AND UPLOAD THE DUMMY DATA
                # df should be set to dummy data. 
            # IF YES, GET LIST OF CSV OBJECTS IN USER DIRECTORY 
                # LOAD LAST CSV OBJECT INTO df VAR.
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("home.html")

# APPLICATION NEWS PAGE - REQUIRES USER TO BE SIGNED IN TO ACCESS    
@app.route('/news/')
def auth_news(): 
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("news.html")

# APPLICATION FAQ PAGE - REQUIRES USER TO BE SIGNED IN TO ACCESS
@app.route('/FAQ/')
def auth_FAQ(): 
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("FAQ.html")

# Define a Flask route for the Dash app's page
#@app.route('/dash/')
#def dash_page():
#    return dash_app.index()

# Run the Flask app
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
