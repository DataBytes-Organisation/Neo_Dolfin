#Creating a model to test and grade the user for payment problems.
import pandas as pd

def pay_probs(transactions):
    # Count the number of months with specific problems
    arrears_count = 0
    declines_count = 0
    dishonours_count = 0
    overlimit_fees_count = 0
    late_fees_count = 0
    payday_loan = False
    
    for _, row in transactions.iterrows():
        balance = row['Balance']
        if balance < 0:
            arrears_count += 1
        if 'decline' in row['Transaction_Type']:
            declines_count += 1
        if 'dishonour' in row['Transaction_Type']:
            dishonours_count += 1
        if 'overlimit_fee' in row['Transaction_Type']:
            overlimit_fees_count += 1
        if 'late_fee' in row['Transaction_Type']:
            late_fees_count += 1
        if 'payday_loan' in row['Transaction_Type']:
            payday_loan = True
    
    # Determine the grade based on the conditions
    if arrears_count >= 6 or (declines_count >= 3 and dishonours_count >= 3):
        grade = 0
    elif (arrears_count >= 2 and arrears_count <= 5) or (declines_count + dishonours_count + overlimit_fees_count >= 9) or late_fees_count >= 3 or payday_loan:
        grade = 1
    elif arrears_count > 0 or declines_count > 0 or dishonours_count > 0 or overlimit_fees_count > 0 or late_fees_count > 0:
        grade = 2
    else:
        grade = 3
    
    # Prepare the output based on the grade
    output = f"User Grade: {grade}\n"
    if grade == 0:
        output += "The user has arrears of 6 or more months or multiple serious problems."
    elif grade == 1:
        output += "The user has arrears of 2-5 months, had declines, dishonours, or overlimit fees 9 or more months, had late fees 3 or more months, had a payday loan, or had multiple moderate problems."
    elif grade == 2:
        output += "The user has fewer months of arrears, declines, dishonours, overlimit fees, or late fees."
    elif grade==3:
        output += "The user has no payment problems."
    
    return output
    
#Testing on a dataset with arrears.
# Load the dataset of bank transactions
transactions_data = pd.read_csv('arrears_transac.csv')

# Grade the user based on the transactions
result = pay_probs(transactions_data)

# Print the output
print(result)