import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime

#Initialize Faker
faker = Faker()

#Load CSV file of merchant names and categories 
descriptions_df = pd.read_csv('neo_dolfin/ai/generated_data/DescriptionsandCategories.csv')

#Define criteria for data/months/income/transactions etc 
num_months = faker.random_int(min=24, max=100)  # Randomly selected number of months
#monthly_income = 6000  # Monthly income deposit
monthly_income = faker.random_int(min=5000, max=7000)
#Starting year for the transactions
start_year = 2022

transactions = [] 
  
#Initialize balance outside the monthly loop to calculate running balance
current_balance = 0  

for month_idx in range(1, num_months + 1):
    year = start_year + (month_idx - 1) // 12  #Calculate year
    month = (month_idx - 1) % 12 + 1  #Calculate month to ensure it's always 1 through 12

    #Income deposit at the beginning of each month
    income_date = datetime(year, month, 1)
    transactions.append({
        'Date': income_date,
        'Transaction Description': 'Monthly Income',
        'Debit': 0,
        'Credit': monthly_income,
        'Balance': current_balance + monthly_income,
        'Category 1': 'Income',
        'Category 2': 'Income',
        'Category 3': 'Wages'
    })
    #Update current balance after adding monthly income
    current_balance += monthly_income  

    # Randomly determine the number of transactions for the current month using faker
    num_transactions = faker.random_int(min=20, max=60)
    dates = sorted([datetime(year, month, faker.random_int(min=2, max=28)) for _ in range(num_transactions)])

    for date in dates:
        # Select a random merchant and corresponding categories
        random_row = descriptions_df.sample(1)
        merchant_name = random_row['Merchant Name'].iloc[0]
        category1 = random_row['Category 1'].iloc[0]
        category2 = random_row['Category 2'].iloc[0]
        category3 = random_row['Category 3'].iloc[0]

        #Use Merchant Name as transaction description
        transaction_description = f"{merchant_name}"

        # Random debit based on a percentage of the current balance (to ensure it doesn't exceed the available funds in the account in one transaction)
        debit = faker.random_int(min=5, max=int(current_balance * 0.1 + 1))

        if debit > current_balance:
            #Insert failed transaction line
            transactions.append({
                'Date': date,
                'Transaction Description': 'Transaction Failed',
                'Debit': 0,
                'Credit': 0,
                'Balance': current_balance,  # Balance remains unchanged
                'Category 1': 'Failed',
                'Category 2': '',
                'Category 3': ''
            })
            # Apply dishonour fee of $15 for a failed transaction 
            date += pd.DateOffset(days=1)  # Assuming the fee is charged the next day
            transactions.append({
                'Date': date,
                'Transaction Description': 'Dishonour Fee',
                'Debit': 15,
                'Credit': 0,
                'Balance': current_balance - 15,
                'Category 1': 'Fee',
                'Category 2': '',
                'Category 3': ''
            })
            current_balance -= 15
        else:
            new_balance = current_balance - debit
            transactions.append({
                'Date': date,
                'Transaction Description': transaction_description,
                'Debit': debit,
                'Credit': 0,
                'Balance': new_balance,
                'Category 1': category1,
                'Category 2': category2,
                'Category 3': category3
            })
            current_balance = new_balance  

#Create DataFrame
df = pd.DataFrame(transactions)

#Add the DR/CR column based on the Debit and CrediT values
df['DR/CR'] = np.where(df['Debit'] > 0, 'DR', 'CR')

#Ensure Date is in datetime format
df['Date'] = pd.to_datetime(df['Date']).dt.date

#Display DataFrame
print(df)

#Save the DataFrame to CSV
df.to_csv('neo_dolfin/ai/generated_data/fake_bank_account_transactions.csv', index=False)
