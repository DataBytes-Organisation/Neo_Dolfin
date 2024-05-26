import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Define variables
monthly_due_date = 5  # Assume the due date is the 5th of each month
monthly_repayment_amount = 100  # Monthly repayment amount in currency
transaction_limit = 1000  # Transaction/account limit in currency
interest_value = 10  # Interest value for late payment in currency
late_payment_value = 50  # Penalty for late payment in currency
loan_amount = 5000  # Loan amount in currency

# Generate personal loan dataset
def generate_personal_loan_data(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    data = {'Date of Transaction': [], 'Description': [], 'Amount': [], 'Balance of Account': [], 'User ID': []}
    balance = loan_amount
    for date in dates:
        # Check if it's the due date
        if date.day == monthly_due_date:
            # Assume a random chance of late payment
            if random.random() < 0.5:  # 50% chance of late payment
                description = 'Late Payment'
                amount = -(monthly_repayment_amount + late_payment_value)
                balance -= monthly_repayment_amount + late_payment_value
            else:
                description = 'Repayment'
                amount = -monthly_repayment_amount
                balance -= monthly_repayment_amount
        else:
            # Assume random transactions throughout the month
            description = 'Charge' if random.random() < 0.5 else 'Transaction'
            amount = random.uniform(-transaction_limit, transaction_limit)
            balance += amount

        data['Date of Transaction'].append(date)
        data['Description'].append(description)
        data['Amount'].append(amount)
        data['Balance of Account'].append(balance)
        data['User ID'].append(random.randint(10000, 99999))  # Generate random user ID

    return pd.DataFrame(data)

# Generate data for two years (24 months)
start_date = datetime(2022, 1, 1)
end_date = datetime(2023, 12, 31)
personal_loan_data = generate_personal_loan_data(start_date, end_date)

# Flag user for debt collection if amount is negative
personal_loan_data['Debt Collection Flag'] = np.where(personal_loan_data['Amount'] < 0, 'Yes', 'No')

# Save data to Excel
personal_loan_data.to_excel('personal_loan_data.xlsx', index=False)
