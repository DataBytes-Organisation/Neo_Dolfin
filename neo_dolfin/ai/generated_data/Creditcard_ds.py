import random
import string
from datetime import datetime, timedelta
import csv

def generate_transaction_description(is_credit):
    if is_credit:
        return 'Monthly Pay'
    stores = ['IKEA', 'Officeworks', 'Amazon', 'Walmart', 'Target', 'Best Buy', 'Costco', 'Starbucks', 'McDonald\'s', 'Subway']
    return random.choice(stores)

def generate_amount():
    return round(random.uniform(0, 1000), 2)

def generate_dataset():
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    dataset = []
    user_ids = ['369', '797']
    balances = {'369': 8000, '797': 8000}
    
    current_date = start_date
    while current_date <= end_date:
        for user_id in user_ids:
            balance = balances[user_id]
            
            if current_date.day == 1:
                # Monthly payment
                transaction_description = 'Monthly Pay'
                debit = 0
                credit = balance
                balance -= credit
            else:
                # Regular transaction
                transaction_description = generate_transaction_description(False)
                amount = generate_amount()
                debit = amount
                credit = 0
                balance += debit
            
            balance = round(balance, 2)
            
            transaction = [user_id, current_date.strftime('%Y-%m-%d'), transaction_description, debit, credit, balance]
            dataset.append(transaction)
            balances[user_id] = balance
        
        current_date += timedelta(days=1)
    
    dataset.sort(key=lambda x: (x[0], x[1]))  # Sort by user_id and date
    return dataset

# Generate the dataset
dataset = generate_dataset()

# Save the dataset to a CSV file
filename = 'credit_card_transactions6.csv'
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['User_ID', 'Date', 'Transaction Description', 'Debit', 'Credit', 'Balance'])
    writer.writerows(dataset)

print(f"Dataset saved to {filename}")