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
import ssl 
import nltk
#import certifi

#import dash
#import dash_core_components as dcc#
#import dash_html_components as html
#test

load_dotenv()  # Load environment variables from .env

from classes import *
from functions import * 
# from ai.chatbot.chatbot_logic import predict_class, get_response, determine_sentiment, listen_to_user, initialize_chatbot_logic
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
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Replace with a secure random key
app.static_folder = 'static'

df = pd.read_csv('static/transaction_ut.csv')

# AWS STUFF
AWS_REGION = os.environ.get('AWS_REGION')
AWS_COGNITO_USER_POOL_ID = os.environ.get('AWS_COGNITO_USER_POOL_ID')
AWS_COGNITO_APP_CLIENT_ID = os.environ.get('AWS_COGNITO_APP_CLIENT_ID')#
AWS_COGNITO_CLIENT_SECRET = os.environ.get('AWS_COGNITO_CLIENT_SECRET')

client = boto3.client('cognito-idp', region_name=AWS_REGION)

# DASH APP
# Initialize Dash app
#dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')  # Set the route to '/dash/'
# Define the Dash layout
#dash_app.layout = dash_layout#

# ROUTING

## LANDING PAGE
@app.route("/") #Initial landing page for application
def landing():
    return render_template('landing.html')

## TERMS OF USE PAGE
@app.route('/TermsofUse') #Terms of Use for application
def TermsofUse():
    return render_template('TermsofUse.html')

## SIGN IN PAGE
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

## SIGN IN USING MFA PAGE
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

            # Grab the user First Name so chatbot can use
            response = client.get_user(
            AccessToken=access_token
            )
            session['given_name']=response['UserAttributes'][3]['Value']

            return redirect('/home/')

        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-in with MFA error: {e}")
            # Handle other sign-up errors
            return render_template('signinmfa.html', form=form, error=e)
    return render_template('signinmfa.html', form=form)

## USER SIGN UP PAGE
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

## SIGN-UP EMAIL CONFIRMATION PAGE
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
        return redirect('signupconf.html', form=form)
    except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"Sign-up Resend Confirmation Email error: {e}")
            # Handle other sign-up errors
            return render_template('signupconf.html', form=form, error='An error occurred. Please try again.')

# ROUTE TO LOG USER OUT FROM AWS AND CLEAR LOCAL CACHE
@app.route('/signout', methods=['GET','POST'] )
def signout():
    try:
        #Clear session / access token at AWS side
        response = client.global_sign_out(
            AccessToken=session.get('access_token')
        )
        #Clear local session info for application
        session.clear()
        return render_template('landing.html')
    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"AWS Cognito sign-out error: {e}")

## REGISTER USER AUTHENTICATION DEVICE PAGE    
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
            return redirect('/signin')
        except Exception as e:
            # Log the error for debugging purposes
            logging.error(f"MFA Device Sign-up error: {e}")
            # Handle other sign-up errors
            return render_template('signupmfad.html', form=form, error='There was an error registering your device. Please try again.')
    return render_template('signupmfad.html', form=form)

## APPLICATION HOME PAGE - REQUIRES USER TO BE SIGNED IN TO ACCESS
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
        # print(request)
        return render_template("home.html")

@app.route('/dash/')
def auth_dash(): 
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("dash.html")


## APPLICATION NEWS PAGE - REQUIRES USER TO BE SIGNED IN TO ACCESS    
@app.route('/news/')
def auth_news(): 
    if not is_token_valid():
        return redirect('/signin')
    if is_token_valid():
        return render_template("news.html")   

## APPLICATION FAQ PAGE - REQUIRES USER TO BE SIGNED IN TO ACCESS
@app.route('/FAQ/')
def auth_FAQ(): 
    if not is_token_valid():
        return redirect('/signin')
    if is_token_valid():
        return render_template("FAQ.html")
    
# APPLICATION TERMS OF USE PAGE 
@app.route('/terms-of-use/')
def open_terms_of_use():
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("TermsofUse.html") 
    
# APPLICATION TERMS OF USE-AI PAGE 
@app.route('/terms-of-use-ai/')
def open_terms_of_use_AI():
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("TermsofUse-AI.html") 
    
# APPLICATION Article Template PAGE 
@app.route('/articleTemplate/')
def open_article_template():
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        return render_template("articleTemplate.html") 
    
# APPLICATION USER SPECIFIC  PROFILE PAGE
@app.route('/profile')
def profile():
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        response = client.get_user(
            AccessToken=session.get('access_token')
        )
        form = UserInfoForm(
            given_name=response['UserAttributes'][3]['Value'],
            family_name=response['UserAttributes'][4]['Value'],
            nickname=response['UserAttributes'][2]['Value'],
            username=response['UserAttributes'][5]['Value']
        )
        return render_template("profile.html", form=form) 
    
# APPLICATION USER RESET PASSWORD PAGE
@app.route('/resetpw', methods=['GET', 'POST'])
def resetpw():
    if not is_token_valid():
        return redirect('/signin')  # Redirect to sign-in page if the token is expired
    if is_token_valid():
        form = ResetPWForm()
        if form.validate_on_submit():
            try:
                response = client.change_password(
                    PreviousPassword=form.oldpassword.data,
                    ProposedPassword=form.newpassword.data,
                    AccessToken=session.get('access_token')
                    )
                # If sign-up is successful, redirect back to profile page
                return redirect('/profile')
                    
            except Exception as e:
                # Log the error for debugging purposes
                logging.error(f"Password Reset Error: {e}")
                # Handle other sign-up errors
                return render_template('resetpw.html', form=form, error='An error occurred. Please try again.')

        return render_template('resetpw.html', form=form)

## CHATBOT PAGE - REQUIRES USER TO BE SIGNED IN TO ACCESS

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if not is_token_valid():
         return redirect('/signin')  # Redirect to sign-in page if the token is expired
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

## Define a Flask route for the Dash app's page
#@app.route('/dash/')
#def dash_page():
#    return dash_app.index()



# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000, debug=True)
