import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime

# Initialize Faker
faker = Faker()

# Settings
num_months = 2  # Number of months for the transactions
num_transactions = 20  # Total number of transactions per month
credit_limit = 5000

transactions = []  # List to store transaction dictionaries
high_value_transaction_limit = int(0.05 * num_transactions * num_months)  # 5% of all transactions
high_value_transactions_count = 0

for month in range(1, num_months + 1):
    current_balance = 0  # Reset balance at the start of each month
    dates = sorted([datetime(2023, month, faker.random_int(min=1, max=27)) for _ in range(num_transactions - 1)])

    for date in dates:
        # Determine max possible debit based on current balance and credit limit
        max_possible_debit = min(credit_limit - current_balance, credit_limit)

        if high_value_transactions_count >= high_value_transaction_limit:
            debit = faker.random_int(min=20, max=250)
        else:
            debit = faker.random_int(min=20, max=max_possible_debit)

        # Ensure debit does not cause balance to exceed credit limit
        debit = min(debit, max_possible_debit)
        
        if debit < 50:
            transaction_description = faker.random_element(elements=('McDonalds', '7/11', 'Coles', 'Yo-Chi', 'Office Works', 'Lune', 'Starbucks', 'Keiths Bakery', 'Junction Cafe'))
        elif 51 <= debit <= 250:
            transaction_description = faker.random_element(elements=('Woolworths', 'Coles', 'Aldi', 'BP Fuel', 'Shell Petrol', 'AGL Electricity', 'Western Water', 'Doctor', 'Dentist'))
        else:
            transaction_description = faker.random_element(elements=('JB Hi Fi', 'IKEA', 'Harvey Norman', 'Adairs'))
            high_value_transactions_count += 1  # Increment the high-value transactions count

        transactions.append({
            'Date': date,
            'Transaction Description': transaction_description,
            'Debit': debit,
            'Credit': 0,
            'Balance': current_balance + debit
        })
        current_balance += debit  # Update current balance

    # Monthly payment transaction on the 28th to reset balance
    payment_date = datetime(2023, month, 28)
    transactions.append({
        'Date': payment_date,
        'Transaction Description': 'Monthly Payment',
        'Debit': 0,
        'Credit': current_balance,  # This payment resets the balance
        'Balance': 0
    })
    current_balance = 0  # Reset balance for next month

# Create DataFrame
df = pd.DataFrame(transactions)

# Add the 'DR/CR' column based on the 'Balance' value
df['DR/CR'] = np.where(df['Balance'] >= 0, 'DR', 'CR')

# Ensure 'Date' is in datetime format
df['Date'] = pd.to_datetime(df['Date']).dt.date

# Display DataFrame
print(df)

# Save the DataFrame to CSV
df.to_csv('fake_credit_card_transactions.csv', index=False)
