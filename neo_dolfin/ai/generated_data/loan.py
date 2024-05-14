import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Define variables
start_date = datetime(2020, 1, 1)
end_date = datetime(2021, 12, 31)
account_number = 'ACC123456789'  # Sample account number

# Generate mock data for the Transaction table for a single user
transaction_data = pd.DataFrame({
    'Transaction ID': ['TRX' + ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=8)) for _ in range(1000)],
    'Account number': [account_number for _ in range(1000)],
    'Transaction date': [start_date + timedelta(days=random.randint(1, 730)) for _ in range(1000)],
    'Transaction time': [datetime.strptime(f"{random.randint(0,23):02d}:{random.randint(0,59):02d}", "%H:%M").time() for _ in range(1000)],
    'Transaction amount': [random.uniform(-1000, 1000) for _ in range(1000)],
    'Credit or debit indicator': [random.choice(['Credit', 'Debit']) for _ in range(1000)],
    'Statement description': ['Transaction ' + str(i) for i in range(1000)],
    'High level transaction purpose': [random.choice(['Shopping', 'Dining', 'Utilities', 'Transportation']) for _ in range(1000)],
    'Mid level transaction purpose': [random.choice(['Online Shopping', 'Restaurant', 'Electricity', 'Gas']) for _ in range(1000)],
    'Low level transaction purpose': [random.choice(['Amazon', 'McDonalds', 'Electricity bill', 'Gas bill']) for _ in range(1000)],
    'Transaction code': [random.randint(1000, 9999) for _ in range(1000)],
    'Merchant ID': [random.randint(100000, 999999) for _ in range(1000)],
    'Previous repayment date': [start_date - timedelta(days=random.randint(1, 30)) for _ in range(1000)]
})

# Update the product type to include random products
transaction_data['Product type'] = [random.choice(['appliances', 'clothing', 'electronics', 'groceries', 'furniture']) for _ in range(1000)]

# Save data to Excel sheet
transaction_data.to_excel('loan.xlsx', index=False)
