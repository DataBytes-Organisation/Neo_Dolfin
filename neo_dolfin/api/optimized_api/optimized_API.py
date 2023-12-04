import requests


class Core:

    def __init__(self, api_key):
        self.api_key = api_key

    def generate_auth_token(self):
        """
        Basiq 3.0 forced. Generate authentication token that will need to be used and passed for all JSON reqs.
        """
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
        """
        Creates a new Basiq user object. Appropriate fields should be passed by partner application\n
        (us), as should duplicate conflicts like mobile and email fields.
        """
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
    def retrieve_user(basiq_id, access_token):
        url = f"https://au-api.basiq.io/users/{basiq_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        return response.text

    @staticmethod
    def update_user_by_dict(basiq_id, user_payload, access_token):
        url = f"https://au-api.basiq.io/users/{basiq_id}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        payload = user_payload

        response = requests.post(url, json=payload, headers=headers)
        return response.text

    @staticmethod
    def update_user(basiq_id, user_first_name, user_last_name, user_email, user_mobile, access_token, user_middle_name=''):
        url = f"https://au-api.basiq.io/users/{basiq_id}"

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
    def create_auth_link(basiq_id, access_token):
        url = f"https://au-api.basiq.io/users/{basiq_id}/auth_link"

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
    def retrieve_auth_link(basiq_id, access_token):
        url = f"https://au-api.basiq.io/users/{basiq_id}/auth_link"

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
    def all_accounts(access_token, basiq_id):
        url = f"https://au-api.basiq.io/users/{basiq_id}/accounts"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        return response.text

    @staticmethod
    def get_account(access_token, basiq_id, account_id):
        url = f"https://au-api.basiq.io/users/{basiq_id}/accounts/{account_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        return response.text

    @staticmethod
    def get_transaction_list(access_token, basiq_id, limit_para, filter_para):
        """
        Get a list of transactions. Auth token and basiq_id required. default list size is 500. filter param is optional.
        Function name differs to reference hyperlink for readabilities sake, else a single 's' is the on difference
        between this and a specific transaction fetch. https://api.basiq.io/reference/gettransactions
        """
        # filter params are not nessecary in default JSON req
        if filter_para != None:
            url = f"https://au-api.basiq.io/users/{basiq_id}/transactions?limit={limit_para}&filter={filter_para}"
        else:
            url = f"https://au-api.basiq.io/users/{basiq_id}/transactions?limit={limit_para}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)
        return response.text

    @staticmethod
    def get_transaction(access_token, basiq_id, transaction_id):
        """
        Get a specific transaction. Auth token, basiq_id required and transaction id required.
        https://api.basiq.io/reference/gettransaction
        """
        
        url = f"https://au-api.basiq.io/users/{basiq_id}/transactions/{transaction_id}"

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
    def get_affordability_report(basiq_id, access_token):
        url = f"https://au-api.basiq.io/users/{basiq_id}/affordability"

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
    def get_expenses(basiq_id, access_token):
        url = f"https://au-api.basiq.io/users/{basiq_id}/expenses"

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
    def get_income(basiq_id, access_token):
        url = f"https://au-api.basiq.io/users/{basiq_id}/income"

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
