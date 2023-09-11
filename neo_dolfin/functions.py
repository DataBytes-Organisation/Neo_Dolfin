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