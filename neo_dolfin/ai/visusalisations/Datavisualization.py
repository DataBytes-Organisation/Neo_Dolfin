# -*- coding: utf-8 -*-
"""

@author: aishwarya
This script shows visulization for the transactional dataset
for a particular user and uses colorbar
to indicate the spending intensity scale, enhancing the interpretability of the color gradient
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# Load the data into a pandas DataFrame
data = pd.read_csv('fake_bank_account_transactions.csv')

# Convert the 'Date' column to datetime format
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Extract the year and month from the 'Date' column
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month

# Calculate the total spending for each month
monthly_spending = data.dropna().groupby(['Year', 'Month'])['Debit'].sum().reset_index()

# Sort the data by year and month
monthly_spending = monthly_spending.sort_values(['Year', 'Month'])

# Create a bar chart
fig, ax = plt.subplots(figsize=(15, 8))
x = [f"{year}-{month:02d}" for year, month in zip(monthly_spending['Year'], monthly_spending['Month'])]
norm = mpl.colors.Normalize(vmin=monthly_spending['Debit'].min(), vmax=monthly_spending['Debit'].max())
colors = plt.cm.viridis(norm(monthly_spending['Debit']))
bars = ax.bar(x, monthly_spending['Debit'], color=colors)
ax.set_xlabel('Month-Year', labelpad=20, weight='bold', size=12)
ax.set_ylabel('Total Spending ($)', labelpad=20, weight='bold', size=12)
ax.set_title('Detailed Monthly Spending Overview', pad=20, weight='bold', size=16)
ax.set_xticks(range(len(x)))
ax.set_xticklabels(x, rotation=45, ha='right')
plt.gca().yaxis.grid(True)

# Create a colorbar
sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label('Spending Intensity ($)', rotation=270, labelpad=20)

# Display the chart
plt.tight_layout()
plt.show()
