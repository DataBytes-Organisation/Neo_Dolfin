
"""
Script for validating various banking and financial data entries using predefined rules.
"""

import re
from datetime import datetime

#-----Utility Functions and Validators Section------

def is_valid_email(email):
    """
    Validate an email using a regular expression pattern to ensure it meets expected format.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_positive_integer(value):
    """
    Check if a value is a positive integer, returning True if so.
    """
    return isinstance(value, int) and value > 0

def is_valid_date(date_str):
    """
    Validate a date string to ensure it is in the YYYY-MM-DD format.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_positive_float(value):
    """
    Check if a value is a positive float, crucial for financial data validation.
    """
    return isinstance(value, float) and value >= 0.0

def is_in_choices(value, choices):
    """
    Verify that a value is within a specified list of choices.
    """
    return value in choices

def has_valid_length(value, min_length=0, max_length=None):
    """
    Ensure a string's length is within a specified minimum and optional maximum length.
    """
    length = len(value)
    if max_length is None:
        return length >= min_length
    return min_length <= length <= max_length

#-----Data Validation Rules Section-----

# Define validation rules for each table in the database
customer_validation_rules = {
    'Customer number': is_positive_integer,
    'Customer age': lambda age: is_positive_integer(age) and age >= 18,
    'Account number': is_positive_integer,
}

account_validation_rules = {
    'Account number': is_positive_integer,
    'Product type': lambda pt: is_in_choices(pt, ['transaction', 'offset', 'savings', 'credit card', 'home loan', 'personal loan']),
    'Account open date': is_valid_date,
    'Account closed date': lambda date: date is None or is_valid_date(date),
    'Account open status': lambda status: is_in_choices(status, ['Open', 'Closed']),
    'Account activate status': lambda status: is_in_choices(status, ['Activated', 'Deactivated']),
    'Snapshot date': is_valid_date,
    'Available credit': is_positive_float,
    'Available FUM': is_positive_float,
}

transaction_validation_rules = {
    'Transaction ID': is_positive_integer,
    'Account number': is_positive_integer,
    'Transaction effective date': is_valid_date,
    'Transaction amount': is_positive_float,
    'Credit or debit indicator': lambda indicator: is_in_choices(indicator, ['Credit', 'Debit']),
    'Statement description': lambda desc: has_valid_length(desc, 1),
    'High level transaction purpose': lambda purpose: has_valid_length(purpose, 1),
    'Mid level transaction purpose': lambda purpose: has_valid_length(purpose, 1),
    'Low level transaction purpose': lambda purpose: has_valid_length(purpose, 1),
    'Transaction code': is_positive_integer,
    'Merchant ID': is_positive_integer,
}

credit_card_validation_rules = {
    'Account number': is_positive_integer,
    'Product type': lambda pt: pt == 'credit card',  # Ensuring product type matches 'credit card' for credit card table
    'Snapshot date': is_valid_date,
    'Statement due day': lambda day: 1 <= day <= 31,  # Assuming day as an integer representing the day of the month
    'Closing balance': is_positive_float,
    'Minimum repayment amount': is_positive_float,
    'Previous repayment date': lambda date: date is None or is_valid_date(date),
    'Previous repayment amount': is_positive_float,
}

loan_validation_rules = {
    'Account number': is_positive_integer,
    'Product type': lambda pt: is_in_choices(pt, ['home loan', 'personal loan']),  # Product type must be either 'home loan' or 'personal loan'
    'Snapshot date': is_valid_date,
    'Payment due day': lambda day: 1 <= day <= 31,  # Assuming day as an integer representing the day of the month
    'Repayment amount': is_positive_float,
    'Previous repayment date': lambda date: date is None or is_valid_date(date),
}

def validate_data(data, validation_rules):
    """
    Apply validation rules to provided data, collecting errors where validations fail.
    """
    errors = {}
    for field, rule in validation_rules.items():
        if not rule(data.get(field, None)):
            errors[field] = f"Invalid value for {field}"
    return errors


#----Data Validation Application Section-----

"""
Below we have sample data entries for demonstration and initial testing of the validation logic.
These examples represent how data will be structured in the 'credit card' and 'loan' tables within the database.
As we transition , real datasets will be introduced later, potentially requiring adjustments to
data ingestion methods (e.g., from CSV files or APIs) to accommodate different data formats and volumes.
"""

# Sample data entry for the credit card table
sample_credit_card = {
    'Account number': 98765,
    'Product type': 'credit card',
    'Snapshot date': '2024-04-10',
    'Statement due day': 15,
    'Closing balance': 1200.50,
    'Minimum repayment amount': 100.00,
    'Previous repayment date': '2024-03-15',
    'Previous repayment amount': 150.00,
}

# Sample invalid data entry for the loan table
sample_loan = {
    'Account number': -2345,
    'Product type': 'home loan',
    'Snapshot date': '2024-04-10',
    'Payment due day': 1,
    'Repayment amount': 500.00,
    'Previous repayment date': '2024-03-01',
}

# Example validation usage for credit card and loan data entries
credit_card_errors = validate_data(sample_credit_card, credit_card_validation_rules)
if credit_card_errors:
    print("Validation errors found in credit card data:", credit_card_errors)
else:
    print("All credit card fields data is valid.")

loan_errors = validate_data(sample_loan, loan_validation_rules)
if loan_errors:
    print("Validation errors found in loan data:", loan_errors)
else:
    print("All loan fields  data is valid.")
