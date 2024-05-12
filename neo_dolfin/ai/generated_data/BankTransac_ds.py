import csv
import random
from datetime import datetime, timedelta

# Read the categories and companies from the CSV file
categories = []
companies = {}
with open('Transaction_Classification_Categories.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        categories.append(row)
        if row[2] not in companies:
            companies[row[2]] = []

# Add specific company names for each category
companies["Transfer"] = ["Bank Transfer", "PayPal", "Venmo"]
companies["Investments"] = ["Stock Purchase"]
companies["Other Income"] = ["Dividend"]
companies["Groceries"] = ["Woolworths", "Coles", "Aldi", "IGA", "Costco"]
companies["Internet"] = ["Telstra", "Optus", "TPG", "iiNet", "Vodafone"]
companies["Maintenance & Improvements"] = ["Bunnings Warehouse", "Home Depot", "Lowe's", "IKEA"]
companies["Pets"] = ["PetSmart", "Petbarn", "Greencross Vets", "RSPCA"]
companies["Rates & Insurance"] = ["RACV", "NRMA", "Allianz", "QBE", "Suncorp"]
companies["Rent & Mortgage"] = ["Real Estate Agency", "Landlord", "Mortgage Lender"]
companies["Utilities"] = ["AGL", "Origin Energy", "EnergyAustralia", "Sydney Water"]
companies["Health & Medical"] = ["Bupa", "Medibank", "NIB", "Chemist Warehouse", "Priceline Pharmacy"]
companies["Children & Family"] = ["Childcare Center", "Toys R Us", "Baby Bunting"]
companies["Clothing & Accessories"] = ["Cotton On", "Uniqlo", "H&M", "Zara", "The Iconic"]
companies["Education"] = ["University", "Online Course Provider", "Tutoring Service"]
companies["Fitness & Wellbeing"] = ["Gym Membership", "Yoga Studio", "Fitness First", "Anytime Fitness"]
companies["Gifts & Donations"] = ["Charity Organization", "GoFundMe", "Birthday Gift"]
companies["Hair & Beauty"] = ["Hair Salon", "Nail Salon", "Sephora", "Mecca", "MAC Cosmetics"]
companies["Life Admin"] = ["Accountant", "Lawyer", "Post Office", "Printing Service"]
companies["Mobile Phone"] = ["Telstra", "Optus", "Vodafone", "Amaysim", "Boost Mobile"]
companies["Public Transport"] = ["Myki", "Opal Card", "TransLink", "Adelaide Metro"]
companies["Parking"] = ["Wilson Parking", "Secure Parking", "City of Melbourne", "Sydney Olympic Park"]
companies["Fuel"] = ["BP", "Shell", "Caltex", "7-Eleven", "United Petroleum"]
companies["Car Insurance, Rego & Maintenance"] = ["RACV", "NRMA", "Allianz", "QBE", "Suncorp"]
companies["Cycling"] = ["Bike Shop", "Cycling Apparel Store", "Bicycle Network"]
companies["Car Repayments"] = ["Car Loan Provider", "Car Dealership", "Toyota Finance"]
companies["Taxies & Share Cars"] = ["Uber", "Ola", "DiDi", "13cabs", "GoCatch"]
companies["Tolls"] = ["CityLink", "EastLink", "Linkt", "E-Toll"]
companies["Restaurants & Cafes"] = ["McDonald's", "KFC", "Hungry Jack's", "Domino's Pizza", "Subway"]
companies["Takeaway"] = ["UberEats", "Deliveroo", "Menulog", "DoorDash", "Domino's Online"]
companies["Events & Gigs"] = ["Ticketek", "Ticketmaster", "Eventbrite", "Moshtix"]
companies["Apps, Games & Software"] = ["Apple App Store", "Google Play Store", "Steam", "Adobe Creative Cloud"]
companies["Alcohol"] = ["Dan Murphy's", "BWS", "First Choice Liquor", "Liquorland"]
companies["Hobbies"] = ["Hobby Store", "Art Supply Store", "Music Store", "Sports Equipment Store"]
companies["Holidays & Travel"] = ["Booking.com", "Airbnb", "Expedia", "Flight Centre", "Qantas"]
companies["Pubs & Bars"] = ["Local Pub", "Cocktail Bar", "Sports Bar", "Rooftop Bar"]
companies["Lottery & Gambling"] = ["Tatts", "TAB", "Sportsbet", "Crown Casino", "The Lott"]
companies["Tobacco & Vaping"] = ["Tobacco Store", "Vape Shop", "Cigars", "Cigarettes"]
companies["Tv, Music & Streaming"] = ["Netflix", "Spotify", "Apple Music", "YouTube Premium", "Stan"]

# Generate fake transaction data
user_ids = [123, 456, 678, 369]
start_date = datetime(2021, 1, 1)
end_date = datetime(2023, 12, 31)

transactions = []
transaction_id = 1
for user_id in user_ids:
    balance = 0
    current_date = start_date
    while current_date <= end_date:
        monthly_transactions = []

        # Credit salary on the 1st of every month
        if current_date.day == 1:
            description = "Salary"
            category = ["Income", "Income", "Wages"]
            credit = 8000
            debit = 0
            balance += credit
            transaction_type = "C"
            transaction = [
                transaction_id,
                user_id,
                current_date.strftime("%Y-%m-%d"),
                description,
                category[0],
                category[1],
                category[2],
                debit,
                credit,
                round(balance, 2),
                transaction_type
            ]
            monthly_transactions.append(transaction)
            transaction_id += 1

        # Generate other transactions for the month
        num_transactions = random.randint(10, 30)
        for _ in range(num_transactions):
            transaction_date = current_date + timedelta(days=random.randint(1, 28))
            if transaction_date > end_date:
                break

            category = random.choice([cat for cat in categories if cat[2] != "Wages"])
            if category[2] == "Investments":
                description = random.choice(companies["Investments"])
                debit = round(random.uniform(100, 1000), 2)
                credit = 0
                balance -= debit
                transaction_type = "D"
            elif category[2] == "Other Income":
                if transaction_date.month == 1 and transaction_date.day == 1:
                    description = random.choice(companies["Other Income"])
                    credit = round(random.uniform(100, 1000), 2)
                    debit = 0
                    balance += credit
                    transaction_type = "C"
                else:
                    continue
            else:
                description = random.choice(companies[category[2]])
                max_expense = min(balance, round(random.uniform(10, 500), 2))
                debit = max_expense
                credit = 0
                balance -= debit
                transaction_type = "D"
            
            transaction = [
                transaction_id,
                user_id,
                transaction_date.strftime("%Y-%m-%d"),
                description,
                category[0],
                category[1],
                category[2],
                debit,
                credit,
                round(balance, 2),
                transaction_type
            ]
            monthly_transactions.append(transaction)
            transaction_id += 1

        # Sort monthly transactions by date
        monthly_transactions.sort(key=lambda x: x[2])

        # Update the balance for each transaction based on the previous balance
        for i in range(1, len(monthly_transactions)):
            prev_balance = monthly_transactions[i-1][9]
            if monthly_transactions[i][10] == "D":
                monthly_transactions[i][9] = round(prev_balance - monthly_transactions[i][7], 2)
            else:
                monthly_transactions[i][9] = round(prev_balance + monthly_transactions[i][8], 2)

        # Add monthly transactions to the main transactions list
        transactions.extend(monthly_transactions)

        current_date = current_date.replace(day=1) + timedelta(days=32)
        current_date = current_date.replace(day=1)

# Save the generated data to a CSV file
output_file = 'fake_transactions8.csv'
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Transaction_ID', 'User_ID', 'Date', 'Description', 'Category 1', 'Category 2', 'Category 3', 'Debit', 'Credit', 'Balance', 'Type'])
    writer.writerows(transactions)

print(f"Fake transaction data saved to {output_file}.")