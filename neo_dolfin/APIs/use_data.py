import time
import os 
import requests
import json
import pandas as pd
from get_data import income
from get_data import expenses
from get_data import afford_report
from get_data import transactions


# Parse the JSON response
income_data = json.loads(income)

# Extract relevant fields from the JSON
data = income_data['regular'] + income_data['irregular'] + income_data['otherCredit']

# Create a list of dictionaries for each record
income_records = []
for item in data:
    record = {
        'source': item['source'],
        'frequency': item['frequency'],
        'ageDays': item['ageDays'],
        'amountAvg': item.get('amountAvg', None),
        'noOccurrences': item.get('noOccurrences', None),
        'avgMonthlyOccurence': item.get('avgMonthlyOccurence', None),
        'currentDate': item['current']['date'],
        'currentAmount': item['current']['amount']
    }
    income_records.append(record)

# Create a Pandas DataFrame from the list of dictionaries
income_df = pd.DataFrame(income_records)


#print(income_df)

#print(expenses)



expense_data = json.loads(expenses)

# Initialize lists to store extracted data
expenses_list = []


# Extract relevant information from the JSON response
for item in expense_data['payments']:
    for sub_category in item['subCategory']:
        for change in sub_category['changeHistory']:
            expense = {
                'division': item['division'],
                'category': sub_category['category']['expenseClass']['classTitle'],
                'date': change['date'],
                'amount': change['amount'],
                'percentageTotal': item['percentageTotal'],
                'avgMonthly': item['avgMonthly']
            }
            expenses_list.append(expense)

# Create a Pandas DataFrame from the extracted data
expenses_df = pd.DataFrame(expenses_list)

# Display the DataFrame
#print(expenses_df)

afford_data = json.loads(afford_report)

#print(afford_data)


trim_afford_data = {
    'fromMonth': afford_data['fromMonth'],
    'toMonth': afford_data['toMonth'],
    'coverageDays': afford_data['coverageDays'],
    'assets': afford_data['summary']['assets'],
    'liabilities': afford_data['summary']['liabilities'],
    'netPosition': afford_data['summary']['netPosition'],
    'creditLimit': afford_data['summary']['creditLimit'],
    'expenses': afford_data['summary']['expenses'],
    'savings': afford_data['summary']['savings'],
    'loanRepaymentsMonthly': afford_data['summary']['loanRepaymentsMonthly'],
    'avgMonthlyIncome': afford_data['summary']['regularIncome']['previous3Months']['avgMonthly']
}

# Create a DataFrame
afford_df = pd.DataFrame([trim_afford_data])

# Display the DataFrame
print(afford_df)

# Parse the JSON response
transaction_data = json.loads(transactions)

#print(transaction_data)

# Extract the list of transactions from the 'data' key
transaction_list = transaction_data['data']

# Extract relevant fields from each transaction
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
        'subClass_title': transaction['subClass']['title'],
        'subClass_code': transaction['subClass']['code']
    }
    transactions.append(transaction)

# Create a DataFrame from the extracted data
transaction_df = pd.DataFrame(transactions)

# Display the DataFrame
print(transaction_df)