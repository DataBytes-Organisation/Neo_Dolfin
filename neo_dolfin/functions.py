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
import datetime
from services.basiq_service import BasiqService
from io import StringIO

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

async def s3connection(bucket_name, s3_client, basiq_service, s3_service):
    success = True
    current_time = datetime.datetime.now().strftime("%m%d%Y%H%M%S")

        # Create default bucket if not exist
    try:
        resp = s3_client.head_bucket(Bucket=bucket_name)
        if resp['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Bucket found")
        else:
            raise Exception("Get bucket failed")
    except Exception:
        print("Default bucket does not exist. Creating bucket")
        s3_client.create_bucket(Bucket = bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'})
        s3_client.create_bucket(Bucket = bucket_name + '-processed', CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'})

        # Check if user has a directory in the S3 bucket
    try:
        df_csv = s3_client.list_objects(Bucket = bucket_name, Prefix = 'raw_data_' + session.get('username'))

    except Exception:
        print("No folder exists for user: " + session.get('username'))
        success = False
            
            # If the user directory does not exist, create that object in the S3 bucket and load the dummy data as a dataframe
    if not success:
        print("Creating object")

            # Get access token for the Basiq API
        access_token = basiq_service.get_access_token()

            # Get all transaction data from Basiq for user and convert to dataframe. Currently returning dummy user data
        user_transaction_data = basiq_service.get_all_transaction_data_for_user(access_token)
        Transactions = pd.json_normalize(user_transaction_data, record_path=['data'])
        df = pd.DataFrame(Transactions)

            # Prepare dataframe data to be set as object in s3 bucket
        csv_buffer = StringIO()
        df.to_csv(csv_buffer)
        testresp = await s3_service.set_object(bucket_name, "raw_data_" + session.get('username') + current_time + ".csv", csv_buffer.getvalue())

            # modified from https://stackoverflow.com/questions/45375999/how-to-download-the-latest-file-of-an-s3-bucket-using-boto3
        get_latest_object = lambda obj: int(obj['LastModified'].strftime('%S'))
            # Get latest object with specific prefix from the processed bucket and set to df2 for savings model
        objects = s3_client.list_objects(Bucket = bucket_name + "-processed", Prefix = "raw_data_" + session.get('username' ))['Contents']  
        latest_object = [obj['Key'] for obj in sorted(objects, key = get_latest_object)][0]
        df2 = pd.read_csv(s3_client.get_object(Bucket = bucket_name + '-processed', Key = latest_object).get('Body'))
  
        #If success, get the latest object and read it into a dataframe
    if success:
            # modified from https://stackoverflow.com/questions/45375999/how-to-download-the-latest-file-of-an-s3-bucket-using-boto3
        get_latest_object = lambda obj: int(obj['LastModified'].strftime('%S'))
        objects = s3_client.list_objects(Bucket = bucket_name, Prefix = "raw_data_" + session.get('username' ))['Contents']    
        latest_object = [obj['Key'] for obj in sorted(objects, key = get_latest_object)][0]
        df1 = pd.read_csv(s3_client.get_object(Bucket = bucket_name, Key = latest_object).get('Body'))
        df2 = s3_client.get_object(Bucket = bucket_name + '-processed', Key = latest_object).get('Body')
        df2 = pd.read_csv(df2)

def loadDatabase(testUser,testId):

    if  testUser:
        df4 = 'static/data/new_data/user' + testId + '.csv'
    else:
        df4 = pd.read_csv('static/data/transaction_ut.csv')
    
    # SQLite User Data Database Setup
    df4.drop(['enrich', 'links'], axis=1, inplace=True) # Drop unnecessary columns
    df4['transactionDate'] = pd.to_datetime(df4['transactionDate'], format='%d/%m/%Y') # Convert 'transactionDate' to datetime format for easy manipulation
    df4['day'] = df4['transactionDate'].dt.day # Create new columns for day, month, and year
    df4['month'] = df4['transactionDate'].dt.month # Create new columns for day, month, and year
    df4['year'] = df4['transactionDate'].dt.year # Create new columns for day, month, and year

    df4['subClass'] = df4.apply(clean_subClass, axis=1) # Clean the 'subClass' column
    df4['subClass'] = df4['subClass'].apply(lambda x: 'Professional and Other Interest Group Services' if x == '{\\title\\":\\"Civic' else x) # Update specific 'subClass' values
    # Check if the SQLite database file already exists
    db_file = "db/transactions_ut.db"
    if not os.path.exists(db_file):
        # If the database file doesn't exist, create a new one
        conn = sqlite3.connect(db_file)
        # Import the cleaned DataFrame to the SQLite database
        df4.to_sql("transactions", conn, if_exists="replace", index=False)
        conn.close()
    else:
        # If the database file already exists, connect to it
        conn = sqlite3.connect(db_file)

