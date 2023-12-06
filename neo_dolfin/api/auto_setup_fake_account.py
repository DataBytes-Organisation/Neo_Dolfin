import os
import requests
from dotenv import load_dotenv
import webbrowser

load_dotenv()
API_KEY = os.getenv("API_KEY")
PHONE = os.getenv("PHONE")


class Fake:
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

        auth_token = response_data["access_token"]  # Get the access token from the JSON data
        return auth_token

    @staticmethod
    def create_fake_user(mobile, access_token):
        url = "https://au-api.basiq.io/users"

        payload = {
            "email": "gavin@hooli.com",
            "mobile": mobile,
            "firstName": "Wentworth",
            "lastName": "Smith"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " f"{access_token}"
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        return response_data.get('id')

    @staticmethod
    def connect_fake_account(user_id, mobile, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/auth_link"

        payload = {
            "mobile": mobile
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " f"{access_token}"
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        return response_data.get('links').get('public')


load_dotenv()
API_KEY = os.getenv("API_KEY")
MOBILE = os.getenv("MOBILE")
api_key = API_KEY
mobile = MOBILE
fake_instance = Fake(api_key)

access_token = fake_instance.get_auth_token()
user_id = fake_instance.create_fake_user(mobile, access_token)
link = fake_instance.connect_fake_account(user_id, mobile, access_token)
webbrowser.open(link)

# Highly recommend use dashboard directly
