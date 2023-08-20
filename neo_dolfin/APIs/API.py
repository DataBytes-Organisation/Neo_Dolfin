import time
import os 
import requests
import json
from dotenv import load_dotenv


#from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env
API_KEY =os.getenv("API_KEY")
user_id = os.getenv("user_id")

## class to manage CORE API's.
class Core:

    def __init__(self, api_key):
        self.api_key = api_key


    def get_auth_token(self):
        url = "https://au-api.basiq.io/token"
        headers = {
            "accept": "application/json",
            "basiq-version": "3.0",
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + self.api_key
        }

        response = requests.post(url, headers=headers)
        response_data = response.json()  # Extract JSON content from the response

        access_token = response_data["access_token"]  # Get the access token from the JSON data
        return access_token
        #response = requests.post(url, headers=headers)
        #access_token = json.loads(response)["access_token"] #strips just the bearer token from the json response
        #return response.text

    def get_user(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}"
    
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " f"{access_token}"
        }
        response = requests.get(url, headers=headers)
        return response.text

    def create_user(self, payload, access_token):
        url = "https://au-api.basiq.io/users"
    
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.text

    def retreive_user(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}"
    
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        return response.text
    
    def update_user(self, user_data, access_token):
        #example user_data
        #"email": "email@gmail.com",
        #"mobile": "+61423330000",
        #"firstName": "First Name",
        #"lastName": "Surname"

        url = f"https://au-api.basiq.io/users/{user_id}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.post(url, json=user_data, headers=headers)

        return response.text

    def create_auth_link(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/auth_link"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)

    def retrieve_auth_link(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/auth_link"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
           return str(e)

## End of CORE Class



class Data:

##__init__
    def __init__(self):
        pass    

#gets all accounts that a user has. Requires user ID and access token.
    def all_accounts(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/accounts"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        return response.text

#returns details on specific account. Requires account_ID and access token. Account ID returned in list of all accounts.
    def get_account(self, user_id, account_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/accounts/{account_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        return response.text
    

#gets last 500 transactions for the user
    def get_transactions(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/transactions"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)
        return response.text

# gets details on a particular transaction
    def get_transaction(self, user_id, transaction_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/transactions/{transaction_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)

#create an affordability summary for a user     
    def get_affordability_report(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/affordability"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)

# create an expense summary for a user
    def get_expenses(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/expenses"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)
        
 # create an income summary for a user   
    def get_income(self, user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/income"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)
        


# Error handling class
class HTTPError(Exception):
    def __init__(self, response):
        self.correlationId = response["correlationId"]
        self.data = response["data"]
        messages = []
        for message in self.data:
            messages.append(message["detail"])
        
        self.msg = ", ".join(messages)

    def get_message(self):
        return self.msg

    def __str__(self):
        return "HTTPError: %s" % self.msg