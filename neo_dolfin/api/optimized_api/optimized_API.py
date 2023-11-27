import requests


class Core:

    def __init__(self, api_key):
        self.api_key = api_key

    def generate_auth_token(self):
        url = "https://au-api.basiq.io/token"

        headers = {
            "accept": "application/json",
            "basiq-version": "3.0",
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + self.api_key
        }

        response = requests.post(url, headers=headers)
        response_data = response.json()

        access_token = response_data["access_token"]
        return access_token

    @staticmethod
    def create_user_by_dict(user_payload, access_token):
        url = "https://au-api.basiq.io/users"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        payload = user_payload

        response = requests.post(url, json=payload, headers=headers)
        return response.text

    @staticmethod
    def create_user(user_first_name, user_middle_name, user_last_name, user_email, user_mobile, access_token):
        url = "https://au-api.basiq.io/users"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        payload = {
            "email": user_email,
            "mobile": user_mobile,
            "firstName": user_first_name,
            "middleName": user_middle_name,
            "lastName": user_last_name
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.text

    @staticmethod
    def retrieve_user(user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        return response.text

    @staticmethod
    def update_user_by_dict(user_id, user_payload, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        payload = user_payload

        response = requests.post(url, json=payload, headers=headers)
        return response.text

    @staticmethod
    def update_user(user_id, user_first_name, user_last_name, user_email, user_mobile, access_token, user_middle_name=''):
        url = f"https://au-api.basiq.io/users/{user_id}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        payload = {
            "email": user_email,
            "mobile": user_mobile,
            "firstName": user_first_name,
            "middleName": user_middle_name,
            "lastName": user_last_name
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.text

    @staticmethod
    def create_auth_link(user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/auth_link"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)

    @staticmethod
    def retrieve_auth_link(user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/auth_link"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)


class Data:

    def __init__(self):
        pass

    @staticmethod
    def all_accounts(user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/accounts"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        return response.text

    @staticmethod
    def get_account(user_id, account_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/accounts/{account_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        return response.text

    @staticmethod
    def get_transactions(user_id, access_token, limit_para=500, filter_para=''):
        url = f"https://au-api.basiq.io/users/{user_id}/transactions?limit={limit_para}&filter={filter_para}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)
        return response.text

    @staticmethod
    def get_transaction(user_id, transaction_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/transactions/{transaction_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)

    @staticmethod
    def get_affordability_report(user_id, access_token):
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

    @staticmethod
    def get_expenses(user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/expenses"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)

    @staticmethod
    def get_income(user_id, access_token):
        url = f"https://au-api.basiq.io/users/{user_id}/income"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return str(e)
