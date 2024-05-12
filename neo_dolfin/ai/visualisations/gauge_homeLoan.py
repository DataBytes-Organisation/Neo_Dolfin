import pandas as pd
import plotly.graph_objects as go

#this graph isn't 100% accurate. In reality, there would be another table that has the life of the loan imported from the users personal accounts
#since we don't have that data i am using the home loan statement i have generated and coming up with a rough calculation of total loan and remaining years


#Dolfin colour scheme codes
dark_grey = '#343a40'
dark_blue = '#0077bb'
grey_1 = '#d9d9d9'
grey_2 = '#fafafe'
grey_3 = '#abb5be'

#import test data for visualisation
file_location = 'neo_dolfin/ai/generated_data/fake_homeloan_data2.csv'
data = pd.read_csv(file_location)
#make sure dates are in date format for calculation
data['Date'] = pd.to_datetime(data['Date'])

#Calculate monthly changes in the balance to use for estimated years left in loan
data['Balance Change'] = data['Balance'].diff().fillna(0)

#Average monthly change
average_change = data['Balance Change'].mean()
#print("Average monthly balance change:", average_change)

#Get the latest balance and calculate how long until the balance is 0 at current rate
current_balance = data['Balance'].iloc[-1]  
months_to_zero = abs(current_balance / average_change)

#Convert months to years for easier understanding
years_to_zero = months_to_zero / 12

#round the values for printing
months_to_zero_rounded = round(months_to_zero)
years_to_zero_rounded = round(years_to_zero)

#find the difference for years past already
start_date =format(min(data['Date']))
statement_end_date = format(max(data['Date']))

from datetime import datetime
min_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
max_date = datetime.strptime(statement_end_date, "%Y-%m-%d %H:%M:%S")
difference_in_years = round((max_date - min_date).days / 365)
#print(f"Exact difference in years: {difference_in_years}")


#reassign all the values to easier to understand labels 
years_passed = difference_in_years
years_left = years_to_zero_rounded  
total_loan_term = years_to_zero_rounded + difference_in_years
#print(years_passed)
#print(years_left)
#print(total_loan_term)  # 

#create the gauge chart 
hl_fig = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = years_left,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Progress on "+str(total_loan_term)+"-Year Home Loan Repayment", 'font': {'size': 24}},
    number = {'suffix': " Years Remaining", 'font': {'size': 20}},
    #delta = {'reference': total_loan_term, 'relative': True, 'valueformat': ".0%"},
    gauge = {
        'axis': {'range': [None, total_loan_term], 'tickwidth': 1, 'tickcolor': '#0077bb'},
        'bar': {'color': '#343a40'},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "white",
        'steps': [
            {'range': [0, years_passed], 'color': '#0077bb'},
            {'range': [years_passed, total_loan_term], 'color': '#343a40'}
        ],
    }
))

#pdate layout
hl_fig.update_layout(paper_bgcolor = "white", font = {'color': '#343a40', 'family': "Arial"})

#Show the figure
hl_fig.show()


