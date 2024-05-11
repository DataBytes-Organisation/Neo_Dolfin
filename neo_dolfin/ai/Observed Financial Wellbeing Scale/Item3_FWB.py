import pandas as pd
import numpy as np

#With reference to the Melbourne Institute Financial Wellbeing Scale 
##https://melbourneinstitute.unimelb.edu.au/__data/assets/pdf_file/0007/4752727/CBA_MI_Tech_Report_No_3.pdf 

#This script is looking to produce item 3 of the scale which identifies months in last year when spending exceeded 80% of inflows - resulting outcomes are one of the following
#score 0 = 11 or 12 months 
#score 1 = 9 or 10 months 
#score 2 = 7 or 8 months 
#score 3 = 4,5, or 6 months 
#score 4 = 3 or less months 

#this only looks at one years worth of data. Script needs to be updated to look at a multi-year csv and filter to only the last year. 


#import the data from csv and store in pandas data frame
#pick the csv with the corresponding score you want to output - this is for testing to show it calculates correctly. 

#file_path = 'neo_dolfin/ai/generated_data/fake_data_item3_score0.csv'
#file_path = 'neo_dolfin/ai/generated_data/fake_data_item3_score1.csv'
#file_path = 'neo_dolfin/ai/generated_data/fake_data_item3_score2.csv'
file_path = 'neo_dolfin/ai/generated_data/fake_data_item3_score3.csv'
#file_path = 'neo_dolfin/ai/generated_data/fake_data_item3_score4.csv'


df = pd.read_csv(file_path)

#convert the Date column to a dateTime format using pandas so the column can be properly read
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')


# Group by year and month
monthly_totals = df.groupby(pd.Grouper(key='Date', freq='M')).agg({
    'Debit': 'sum',
    'Credit': 'sum'
}).reset_index()

# Rename columns for clarity
monthly_totals.rename(columns={'Date': 'Month'}, inplace=True)

#calculate the percentage of debits to credits each month
monthly_totals['Debit_Percentage'] = (monthly_totals['Debit'] / monthly_totals['Credit']) * 100

#identify months where spending exceeded 80% of inflows
exceeds_80 = monthly_totals['Debit_Percentage'] > 80
count_exceeds_80 = exceeds_80.sum()

# Define outcomes using number of exceeded months to specific outputs
def exceeded_months_to_score(count):
    if count >= 11:
        return 0
    elif count >= 9:
        return 1
    elif count >= 7:
        return 2
    elif count >= 4:
        return 3
    else:
        return 4

# Get the output based on the count of exceeded months
output = exceeded_months_to_score(count_exceeds_80)
print(f"Score: {output}")





