import pandas as pd
import random
from datetime import datetime, timedelta

def generate_home_loan_dataset():
    data = []
    user_ids = [369, 797]
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)

    for user_id in user_ids:
        current_date = start_date
        if user_id == 369:
            balance = 500000
            interest_amount = 2200
            repayment_amount = 1500
        else:  # user_id == 797
            balance = 700000
            interest_amount = 2800
            repayment_amount = 3000

        data.append([user_id, start_date.strftime("%Y-%m-%d"), "Opening Balance", 0, balance, balance, "Credit"])

        while current_date <= end_date:
            if current_date.day == 15:
                balance += interest_amount
                data.append([user_id, current_date.strftime("%Y-%m-%d"), "Interest Applied", 0, interest_amount, balance, "Credit"])

            if current_date.day == 10 or current_date.day == 20:
                balance -= repayment_amount
                data.append([user_id, current_date.strftime("%Y-%m-%d"), "Loan Repayment", repayment_amount, 0, balance, "Debit"])

            current_date += timedelta(days=1)

    df = pd.DataFrame(data, columns=["User_Id", "Date", "Transaction_Description", "Debit", "Credit", "Balance", "Type"])
    df.fillna(0, inplace=True)
    return df

# Generate the dataset
df = generate_home_loan_dataset()

# Save the dataset to a CSV file
csv_file_path = "home_loan_dataset3.csv"
df.to_csv(csv_file_path, index=False)

print(f"Dataset saved to {csv_file_path}")