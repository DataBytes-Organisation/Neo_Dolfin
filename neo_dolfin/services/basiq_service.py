import boto3 as boto3
from dotenv import load_dotenv
import os
from services.Interfaces.ibasiq_service import IBasiqService
import requests
import json
import datetime

# Methods adapted from Trimester 1 Dolfin code to suit our use case
load_dotenv()  # Load environment variables from .env
BASE_URL = os.environ.get('BASE_URL')
BASIQ_ID = os.environ.get('BASIQ_ID')
API_KEY = os.environ.get('API_KEY')

s3 = boto3.client('s3')

url = f"{BASE_URL}users/{BASIQ_ID}/transactions"

class BasiqService(IBasiqService):
    def __init__(self):
        self._data_source = []

    def get_access_token(self):
            url = BASE_URL + "token"
            payload = "scope=SERVER_ACCESS"
            headers = {
                "accept": "application/json",
                "basiq-version": "3.0",
                "content-type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {API_KEY}"
            }

            response = requests.post(url, data=payload, headers=headers)
            json_response = response.json()
            access_token = "Bearer " + json_response["access_token"]
            return access_token

    def create_user_transaction_data_object(data, username, bucket_name, file_name):
        #Add exception handling
        current_time = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        
        return s3.put_object(Body = data, Bucket = bucket_name, Key = username + "/" + file_name + current_time)
        
    def get_headers(self, access_token):
        headers = {
                "accept": "application/json",
                "authorization": access_token,
        }
        
        return headers

    def get_all_transaction_data_for_user(self, access_token):
        headers = self.get_headers(access_token)
            
        response = requests.get(url, headers=headers)
        return json.loads(response.text)