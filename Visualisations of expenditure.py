#!/usr/bin/env python
# coding: utf-8

# In[6]:


#Orignal data based on fake generated data.

import pandas as pd
import matplotlib.pyplot as plt


# In[11]:


def plot_financial_overview_for_user(user_id, file_path):
    import pandas as pd
    import matplotlib.pyplot as plt

    # Load the data from the specified Excel file
    data = pd.read_excel(file_path)
    
    # Ensure 'Date' is in datetime format
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Add a 'User ID' field if it does not exist
    if 'User ID' not in data.columns:
        data['User ID'] = range(1, len(data) + 1)
    
    # Filter data for the specified user ID
    user_data = data[data['User ID'] == user_id]
    
    if user_data.empty:
        print(f"No data available for User ID: {user_id}")
        return

    # Define color scheme
    colors = {"Credit": "#0077bb", "Debit": "#d9d9d9", "Balance": "#343a40", "Text": "#abb5be"}

    # Plotting bars
    # Define positions for the groups
    bar_width = 0.15  # Slimmer bars
    r1 = range(len(user_data))
    r2 = [x + bar_width for x in r1]
    r3 = [x + 2 * bar_width for x in r1]

    # Create bars
    plt.figure(figsize=(14, 7))
    plt.bar(r1, user_data['Credit'], color=colors['Credit'], width=bar_width, edgecolor='grey', label='Credit')
    plt.bar(r2, user_data['Debit'], color=colors['Debit'], width=bar_width, edgecolor='grey', label='Debit')
    plt.bar(r3, user_data['Balance'], color=colors['Balance'], width=bar_width, edgecolor='grey', label='Balance')
    
    # Add xticks on the middle of the group bars
    plt.xlabel('Date', fontweight='bold')
    plt.xticks([r + bar_width for r in range(len(user_data))], user_data['Date'].dt.strftime('%Y-%m-%d'))
    
    # Adding labels and title
    plt.ylabel('Amount')
    plt.title(f'Financial Overview for User ID: {user_id}')

    # Display category information in light-toned colors
    category_info = f"Categories:\nCategory 1: {user_data['Category 1'].unique()}\nCategory 2: {user_data['Category 2'].unique()}\nCategory 3: {user_data['Category 3'].unique()}"
    plt.figtext(0.915, 0.5, category_info, ha="center", va="center", fontsize=10, bbox={"boxstyle":"round", "facecolor":colors['Text']})
    
    # Adjust layout to make room for category information
    plt.subplots_adjust(right=0.85)
    
    # Create legend & Show graphic
    plt.legend()
    plt.show()

# Example usage:
# plot_financial_overview_for_user(1, 'fake_bank_account_transactions2 1.xlsx')


# In[8]:


plot_financial_overview_for_user(2, 'fake_bank_account_transactions2 1.xlsx')


# In[13]:


def plot_category_summary(file_path):
    import pandas as pd
    import matplotlib.pyplot as plt

    # Load the data from the specified Excel file
    data = pd.read_excel(file_path)
    
    # Calculate totals for Category 1
    category1_totals = data.groupby(['Category 1']).agg({'Debit': 'sum', 'Credit': 'sum'})
    category2_totals = data.groupby(['Category 2']).agg({'Debit': 'sum', 'Credit': 'sum'})

    # Define color scheme
    colors = ["#0077bb", "#d9d9d9"]  # Blue for Credit, Gray for Debit

    # Plotting for Category 1
    plt.figure(figsize=(10, 6))
    category1_totals.plot(kind='bar', color=colors, width=0.8)
    plt.title('Income vs Expenditure for Category 1')
    plt.ylabel('Amount')
    plt.xlabel('Category')
    plt.xticks(rotation=0)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(['Debit', 'Credit'])
    plt.tight_layout()

    # Plotting for Category 2
    plt.figure(figsize=(10, 6))
    category2_totals.plot(kind='bar', color=colors, width=0.8)
    plt.title('Income vs Expenditure for Category 2')
    plt.ylabel('Amount')
    plt.xlabel('Category')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(['Debit', 'Credit'])
    plt.tight_layout()

    plt.show()

# Example usage:
plot_category_summary('fake_bank_account_transactions2 1.xlsx')


# In[15]:


def plot_by_category_selection_interactive(file_path):
    import pandas as pd
    import matplotlib.pyplot as plt

    # Load the data from the specified Excel file
    data = pd.read_excel(file_path)
    
    # Get unique values for Category 1 and Category 2 for user to choose from
    category1_options = data['Category 1'].unique()
    category2_options = data['Category 2'].unique()
    
    # Display options and prompt user for input
    print("Available Category 1 options:", category1_options)
    category1_selection = input("Select a category from Category 1: ")
    
    print("Available Category 2 options:", category2_options)
    category2_selection = input("Select a category from Category 2: ")

    # Filter data based on user selection
    filtered_data = data[(data['Category 1'] == category1_selection) & (data['Category 2'] == category2_selection)]
    
    if filtered_data.empty:
        print(f"No data available for Category 1: {category1_selection} and Category 2: {category2_selection}")
        return

    # Group by Category 3 and calculate totals
    category3_totals = filtered_data.groupby('Category 3').agg({'Debit': 'sum', 'Credit': 'sum'})

    # Define color scheme
    colors = ["#0077bb", "#d9d9d9"]  # Blue for Credit, Gray for Debit

    # Plotting results
    plt.figure(figsize=(10, 6))
    category3_totals.plot(kind='bar', color=colors, width=0.8)
    plt.title(f'Income vs Expenditure for {category1_selection} - {category2_selection}')
    plt.ylabel('Amount')
    plt.xlabel('Category 3')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(['Debit', 'Credit'])
    plt.tight_layout()
    
    plt.show()


plot_by_category_selection_interactive('fake_bank_account_transactions2 1.xlsx')


# In[ ]:




