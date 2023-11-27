import pandas as pd
import re
import sqlite3
import plotly.graph_objects as go
import os

# Querying Functions
# Function to get the true ending balance for a specific month and year
def get_last_balance_for_month_year(conn, month, year):
    cursor = conn.cursor()
    cursor.execute(f"SELECT balance FROM transactions WHERE month = ? AND year = ? ORDER BY transactionDate DESC, id DESC LIMIT 1", (month, year))
    result = cursor.fetchone()
    final_balance = result[0] if result else 0
    return final_balance

# Function to get total spending/saving for a specific month and year
def get_total_amount_for_month_year(conn, direction, month, year):
    cursor = conn.cursor()
    cursor.execute(f"SELECT SUM(amount) FROM transactions WHERE direction = ? AND month = ? AND year = ?", (direction, month, year))
    result = cursor.fetchone()
    total_amount = result[0] if result[0] is not None else 0
    
    # Get the true ending balance for the month and year, irrespective of direction
    cursor.execute(f"SELECT balance FROM transactions WHERE month = ? AND year = ? ORDER BY transactionDate DESC, id DESC LIMIT 1", (month, year))
    result = cursor.fetchone()
    final_balance = result[0] if result else 0
    
    return total_amount, final_balance

# Function to get total spending/saving for a specific year and plot it
def plot_total_amount_for_year(conn, direction, year):
    cursor = conn.cursor()
    cursor.execute(f"SELECT month, SUM(amount), MAX(balance) FROM transactions WHERE direction = ? AND year = ? GROUP BY month", (direction, year))
    data = cursor.fetchall()
    
    months = [x[0] for x in data]
    amounts = [x[1] for x in data]
    balances = [x[2] for x in data]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=amounts, mode='lines+markers', name=f'{direction.capitalize()} Amount'))
    fig.add_trace(go.Scatter(x=months, y=balances, mode='lines+markers', name='Balance'))
    fig.update_layout(title=f"{direction.capitalize()} and Balance in {year}", xaxis_title="Month", yaxis_title="Amount/Balance")
    fig.show()

# Function to get total spending/saving for a range of months and years and plot it
def plot_total_amount_for_range(conn, direction, start_month, start_year, end_month, end_year):
    cursor = conn.cursor()
    
    if start_year == end_year:
        query = """
        SELECT month, year, SUM(amount), MAX(balance)
        FROM transactions
        WHERE direction = ? AND year = ? AND month >= ? AND month <= ?
        GROUP BY month, year
        ORDER BY year, month
        """
        cursor.execute(query, (direction, start_year, start_month, end_month))
    else:
        query = """
        SELECT month, year, SUM(amount), MAX(balance)
        FROM transactions
        WHERE direction = ?
        AND (
            (year = ? AND month >= ?) OR
            (year = ? AND month <= ?) OR
            (year > ? AND year < ?)
        )
        GROUP BY month, year
        ORDER BY year, month
        """
        cursor.execute(query, (direction, start_year, start_month, end_year, end_month, start_year, end_year))
    
    data = cursor.fetchall()
    
    dates = [f"{x[0]}-{x[1]}" for x in data]
    amounts = [x[2] for x in data]
    balances = [x[3] for x in data]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=amounts, mode='lines+markers', name=f'{direction.capitalize()} Amount'))
    fig.add_trace(go.Scatter(x=dates, y=balances, mode='lines+markers', name='Balance'))
    fig.update_layout(title=f"{direction.capitalize()} and Balance from {start_month}-{start_year} to {end_month}-{end_year}", xaxis_title="Month-Year", yaxis_title="Amount/Balance")
    fig.show()


# Function to get the transaction with the highest amount in the last month or year
def get_highest_spending_last_period(conn, period, num, year=None):
    cursor = conn.cursor()
    if period == 'month':
        query = "SELECT description, subClass, amount FROM transactions WHERE direction = 'debit' AND month = ? AND year = ? ORDER BY amount ASC LIMIT 1"
        cursor.execute(query, (num, year))
    elif period == 'year':
        query = "SELECT description, subClass, amount FROM transactions WHERE direction = 'debit' AND year = ? ORDER BY amount ASC LIMIT 1"
        cursor.execute(query, (num,))
        
    data = cursor.fetchone()
    
    if data:
        if year:
            formatted_output = f"Highest Spending in {num}, {year}: {data[0]} (Category: {data[1]}) with amount {data[2]}"
        else:
            formatted_output = f"Highest Spending in {num}: {data[0]} (Category: {data[1]}) with amount {data[2]}"
    else:
        formatted_output = "No data found for the specified period."
    
    cursor.close()
    return formatted_output


##
def get_total_positive_amount_for_month_year(conn, month, year):
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE amount > 0 AND month = ? AND year = ?", (month, year))
    result = cursor.fetchone()
    total_positive_amount = result[0] if result[0] is not None else 0
    return total_positive_amount


def get_total_negative_amount_for_month_year(conn, month, year):
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE amount < 0 AND month = ? AND year = ?", (month, year))
    result = cursor.fetchone()
    total_negative_amount = result[0] if result[0] is not None else 0
    return total_negative_amount


def get_total_negative_amount_for_year(conn, year):
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE amount < 0 AND year = ?", (year,))
    result = cursor.fetchone()
    total_negative_amount = result[0] if result[0] is not None else 0
    return total_negative_amount
##


# Test the functions
#print(get_total_amount_for_month_year(conn, 'credit', 6, 2023))
#print(get_total_amount_for_month_year(conn, 'debit', 6, 2023))
#print(get_last_balance_for_month_year(conn, 6, 2023))

#plot_total_amount_for_year(conn, 'debit', 2022)  # Uncomment this line when running locally to see the plot
# plot_total_amount_for_range(conn, 'credit', 4, 2022, 11, 2022)  # Uncomment this line when running locally to see the plot
# print(get_highest_spending_last_period(conn, 'month', 7, 2023))
