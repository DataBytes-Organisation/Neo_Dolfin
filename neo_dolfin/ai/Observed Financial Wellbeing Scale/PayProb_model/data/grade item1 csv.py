import csv
from datetime import datetime

def calculate_payment_problem_grade(row, current_date):
    # Convert postDate string to datetime object
    post_date = datetime.strptime(row['postDate'], '%Y-%m-%dT%H:%M:%SZ')

    # Calculate the difference in months
    months_difference = (current_date.year - post_date.year) * 12 + current_date.month - post_date.month

    # Determine the payment problem grade based on the time span
    if months_difference >= 6:
        return 0
    elif 2 <= months_difference <= 5:
        return 1
    elif 1 <= months_difference:
        return 2
    else:
        return 3

def mark_payment_problem(input_file, output_file):
    with open(input_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['paymentProblemGrade']
        data = []
        sorted_transactions = sorted(reader, key=lambda x: datetime.strptime(x['postDate'], '%Y-%m-%dT%H:%M:%SZ'))
        current_date = datetime.now()
        for row in sorted_transactions:
            # Check if it's a debit transaction and if the amount is less than 0
            if row['direction'] == 'debit' and float(row['amount']) < 0:
                # Check if the description indicates a payment problem
                description = row['description'].lower()
                if 'payment problems' in description or 'payment problem' in description:
                    row['paymentProblemGrade'] = 0
                else:
                    # Calculate the payment problem grade based on the time span
                    row['paymentProblemGrade'] = calculate_payment_problem_grade(row, current_date)
            else:
                row['paymentProblemGrade'] = 3
            data.append(row)

    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Example usage:
input_file = 'fake_financial_data_dependent_on_balance.csv'
output_file = 'marked_financial_data_with_grades.csv'
mark_payment_problem(input_file, output_file)
print(f"Payment problem grades marked and saved to {output_file}")
