import pandas as pd
import numpy as np
from datetime import datetime, timedelta

number_of_interest_applied = 24
number_of_loan_payments = number_of_interest_applied *2

#Define the opening balance and date
opening_balance = pd.DataFrame({
    'Date': [datetime(2022, 12, 30)],
    'Transaction Description': ['Opening Balance'],
    'Debit': [0],
    'Credit': [0],
    'Balance': [639000]
})

#Generate dates every 14 days for the initial data
loan_repayments = pd.DataFrame({
    'Date': [datetime(2023, 1, 1) + timedelta(days=i*14) for i in range(number_of_loan_payments)],
    'Transaction Description': ['Loan Repayments']*number_of_loan_payments,
    'Debit': [0]*number_of_loan_payments,
    'Credit': [1637]*number_of_loan_payments,
    'Balance': [0]*number_of_loan_payments  # Placeholder, to be calculated
})

#Generate the additional 24 monthly rows for interest
interest_applied = pd.DataFrame({
    'Date': [datetime(2022, 12, 30) + pd.DateOffset(months=i) for i in range(number_of_interest_applied)],
    'Transaction Description': ['Interest Applied']*number_of_interest_applied,
    'Debit': [2400]*number_of_interest_applied,
    'Credit': [0]*number_of_interest_applied,
    'Balance': [0]*number_of_interest_applied  # Placeholder, to be calculated
})

#Combine all parts into one DataFrame
dates_df = pd.concat([opening_balance, loan_repayments, interest_applied])

#Sort the DataFrame by date
dates_df.sort_values(by='Date', inplace=True)

#Calculate the running balance
dates_df.reset_index(drop=True, inplace=True)
dates_df.loc[0, 'Balance'] = 639000  # Reset opening balance
dates_df['Balance'] = dates_df['Balance'].cumsum() - dates_df['Credit'].cumsum() + dates_df['Debit'].cumsum()

#Add the 'DR/CR' column based on the 'Balance' value
dates_df['DR/CR'] = np.where(dates_df['Balance'] >= 0, 'DR', 'CR')

#Ensure 'Date' is in datetime format just for display consistency
dates_df['Date'] = pd.to_datetime(dates_df['Date']).dt.date

#Display the DataFrame
print(dates_df)
 
 #export to csv 
dates_df.to_csv('neo_dolfin/ai/generated_data/fake_homeloan_data.csv', index=False)