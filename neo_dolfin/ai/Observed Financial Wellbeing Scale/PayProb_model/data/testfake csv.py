import csv
import uuid
import random
from datetime import datetime, timedelta

# List of transaction descriptions
transaction_descriptions = [
    "Manly Maths Tutor Wages",
    "Non Hooli ATM Withdrawal Fee",
    "Wdl ATM WESTPAC IGA BALGOWLAH BALGOWL AU",
    "TFR Acc14000 TO 12389",
    "CTRLINK CARERS Ref: 998R6789201610974V",
    "AGL RETAIL ENERGY LTD (GAS)",
    "TRANSFER TO JOANNA SMITH CAMPING",
    "Transfer Platnm Homeloan 346454",
    "Payroll WFRMS 15439393",
    "Netflix Subscription",
    "Uber Ride",
    "Amazon Online Shopping",
    "Gasoline Purchase",
    "Electricity Bill Payment",
    "Mobile Phone Bill Payment",
    "Restaurant Dinner",
    "Coffee Shop Purchase",
    "Gym Membership Fee",
    "Hair Salon Appointment",
    "Movie Ticket Purchase",
    "Online Gaming Purchase",
    "Bookstore Purchase",
    "Clothing Store Purchase",
    "Home Improvement Store Purchase",
    "Pharmacy Purchase",
    "Car Maintenance Expense",
    "Public Transport Fare",
    "Travel Agency Booking",
    "Music Streaming Subscription"
]

def generate_fake_data(num_clients, num_transactions_per_client):
    data = []
    for _ in range(num_clients):
        # Initialize balance for each client
        balance = round(random.uniform(5000, 20000), 2)
        for _ in range(num_transactions_per_client):
            transaction_id = str(uuid.uuid4())
            status = "posted"  # All transactions are considered posted
            description = random.choice(transaction_descriptions)  # Randomly choose a transaction description
            # Generate positive amount for payroll income and negative amount for expenses
            if description.startswith("Payroll WFRMS"):
                amount = round(random.uniform(10000, 12000), 2)  # Payroll income
            else:
                amount = round(random.uniform(0, -5000), 2)  # Expense
            account = str(uuid.uuid4())  # Fake account ID
            direction = "debit" if amount < 0 else "credit"  # Determine transaction direction
            class_ = "transfer" if direction == "credit" else random.choice(["bank-fee", "cash-withdrawal", "payment"])
            institution = "AU00000"  # Fake institution code
            post_date = fake_post_date()  # Generate fake post date
            
            # Update balance based on transaction amount and direction
            balance += amount  # Expenses reduce balance, income increases balance

            data.append({
                'type': 'transaction',
                'id': transaction_id,
                'status': status,
                'description': description,
                'amount': abs(amount) if direction == "credit" else amount,  # Amount column contains only positive values for credits
                'account': account,
                'balance': round(balance, 2),  # Round balance to two decimal points
                'direction': direction,
                'class': class_,
                'institution': institution,
                'postDate': post_date
            })
    return data


def fake_post_date():
    # Generate a random date within the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date.strftime('%Y-%m-%dT%H:%M:%SZ')

def write_data_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as file:
        fieldnames = ['type', 'id', 'status', 'description', 'amount', 'account', 'balance', 'direction', 'class', 'institution', 'postDate']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Generate fake data for 500-1000 clients with transactions dependent on balance
num_clients = random.randint(500, 1000)
num_transactions_per_client = 10  
fake_data = generate_fake_data(num_clients, num_transactions_per_client)

# Write fake data to CSV file
file_path = 'fake_financial_data_dependent_on_balance.csv'
write_data_to_csv(fake_data, file_path)
print(f"Fake data generated and saved to {file_path}")
