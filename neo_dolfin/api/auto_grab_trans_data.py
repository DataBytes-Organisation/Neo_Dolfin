from API import Core, Data
import os
from dotenv import load_dotenv
import json
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()
API_KEY = os.getenv("API_KEY")
user_id = os.getenv("user_id")

api_key = API_KEY
core_instance = Core(api_key)
data_instance = Data()

access_token = core_instance.get_auth_token()

transactions = data_instance.get_transactions(user_id, access_token)

tran_data = json.loads(transactions)

transaction_list = tran_data['data']

transactions = []
for transaction in transaction_list:
    transaction = {
        'type': transaction['type'],
        'id': transaction['id'],
        'status': transaction['status'],
        'description': transaction['description'],
        'amount': transaction['amount'],
        'account': transaction['account'],
        'balance': transaction['balance'],
        'direction': transaction['direction'],
        'class': transaction['class'],
        'institution': transaction['institution'],
        'postDate': transaction['postDate'],
        'subClass_title': transaction['subClass']['title'] if transaction.get('subClass') else None,
        'subClass_code': transaction['subClass']['code'] if transaction.get('subClass') else None
    }
    transactions.append(transaction)

# Create a DataFrame from the extracted data
transaction_df = pd.DataFrame(transactions)
transaction_df.to_csv('user7.csv', index=False)

transaction_df['postDate'] = pd.to_datetime(transaction_df['postDate'])
transaction_df.sort_values(by='postDate', inplace=True)
plt.figure(figsize=(10, 6))
plt.plot(transaction_df['postDate'], transaction_df['balance'], marker='o')
plt.title('Balance vs. Time')
plt.xlabel('Date')
plt.ylabel('Balance')
plt.show()