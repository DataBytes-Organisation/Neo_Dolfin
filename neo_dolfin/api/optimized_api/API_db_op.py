import sqlite3
from .optimized_API import Core, Data
import os
from dotenv import load_dotenv
import json
import webbrowser
import pandas as pd
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")
api_key = API_KEY
core_instance = Core(api_key)
data_instance = Data()
access_token = core_instance.generate_auth_token()
user_db_path = "db/user_database.db"
transactions_db_path = "transactions_ut.db"

## Operations specifically for interacting with the Dolfin Database, using functions from optimized_API.py

# Operations specifically for interacting with the Dolfin Database
def init_dolfin_db():
    """
    Initialize the DolFin database and create user and transaction tables.
    Connects to the SQLite database and sets up foreign key constraints.
    Creates users and transactions tables if they don't exist.
    """
    try:
        with sqlite3.connect(user_db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users_new
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username VARCHAR(30),
                 email VARCHAR(255),
                 mobile VARCHAR(12),
                 first_name VARCHAR(255),
                 middle_name VARCHAR(255),
                 last_name VARCHAR(255),
                 password VARCHAR(255),
                 pwd_pt VARCHAR(255),
                 b_id_temp VARCHAR(36) DEFAULT NULL);
            ''')
            # transactions will be handled in transactions_ut.db for now
           
            return "INITIALISE - Connected to Dolfin Database."
    except sqlite3.Error as e:
        return "INITIALSIE - An error occurred: " + str(e)


def register_user(username, email, mobile, first_name, middle_name, last_name, password):
    """
    Registers a new DolFin user.
    Inserts user information into the users_new table.
    Parameters include username, email, mobile number, first name, middle name, last name, and password.
    """
    try:
        with sqlite3.connect(user_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users_new (username, email, mobile, first_name, middle_name, last_name, password)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (username, email, mobile, first_name, middle_name, last_name, password))
            conn.commit()
            return "USER REGISTRATION: User \"%s %s\" inserted successfully into 'users_new' table." %(first_name, last_name)
    except sqlite3.Error as e:
        return "USER REGISTRATION - An error occurred: " + str(e)


def get_basiq_id(username):
    """
    Retrieves the basiq ID for a specific DolFin user.
    Queries the users_new table for the basiq ID based on the user ID.
    """
    try:
        with sqlite3.connect(user_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT b_id_temp FROM users_new WHERE username = ?",(username,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return "FETH BASIQ ID - No user found with the given ID."
    except sqlite3.Error as e:
        return "FETCH BASIQ ID - An error occurred: " + str(e)


def get_user_info(user_id):
    """
    Retrieves information of a DolFin user in a dictionary.
    Queries for basic information of a user by user ID, including email, mobile, first name, middle name, and last name.
    """
    try:
        with sqlite3.connect(user_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email, mobile, first_name, middle_name, last_name FROM users_new WHERE id = ?",(user_id,))
            result = cursor.fetchone()
            if result:
                user_info = {
                    "email":        result[0],
                    "mobile":       result[1],
                    "firstName":    result[2],
                    "middleName":   result[3],
                    "lastName":     result[4]
                }
                return user_info
            else:
                return "USER INFO - No user found with the given ID."
    except sqlite3.Error as e:
        return "USER INFO - An error occurred: " + str(e)


def register_basiq_id(user_id):
    """
    Registers a basiq ID for a DolFin user.
    Generates a basiq ID based on user information and updates the basiq ID field in the users table.
    """
    try:
        new_basiq_id = json.loads(core_instance.create_user_by_dict(get_user_info(user_id), access_token)).get('id')
        with sqlite3.connect(user_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users_new SET b_id_temp = ? WHERE id = ?", (new_basiq_id, user_id))
            if cursor.rowcount == 0:
                return "No user found with the given ID."
            conn.commit()
            return "BASIQ REGISTER: basiq_id updated successfully for user ID {}".format(user_id)
    except sqlite3.Error as e:
        return "BASIQ REGISTER - An error occurred: " + str(e)


def link_bank_account(user_id):
    """
    Link a DolFin user to their bank accounts.
    Generates an authorization link based on the user's basiq ID and opens it in a web browser.
    """
    try:
        with sqlite3.connect(user_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT b_id_temp FROM users_new WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                link = json.loads(core_instance.create_auth_link(result[0], access_token)).get('links').get('public')
                webbrowser.open(link)
                # ^^^ a html popup that informs the user that they need to go link their account in the new tab should popup here so the user knows what they need to do now
            else:
                return "AUTH LINK - No user found with the given ID."
    except sqlite3.Error as e:
        return "AUTH LINK - An error occurred: " + str(e)


def request_transactions_df(user_id, limit_para=500, filter_para=None):
    """
    Requests and returns user transaction data in DataFrame format.
    Fetches the transaction list based on the user's basiq ID and converts it into a DataFrame.
    """
    tran_data = json.loads(data_instance.get_transaction_list(access_token, get_basiq_id(user_id), limit_para, filter_para))
    transaction_list = tran_data['data']
    
    transactions = []
    for transaction in transaction_list:
        date_obj = datetime.fromisoformat(transaction['postDate'])
        post = date_obj.strftime("%Y-%m-%d")
        date_obj = datetime.fromisoformat(transaction['postDate'])
        tran = date_obj.strftime("%Y-%m-%d")
        transaction = {
            'id':               transaction['id'],
            'type':             transaction['type'],
            'status':           transaction['status'],
            'description':      transaction['description'],
            'amount':           transaction['amount'],
            'account':          transaction['account'],
            'balance':          transaction['balance'],
            'direction':        transaction['direction'],
            'class':            transaction['class'],
            'institution':      transaction['institution'],
            'transactionDate':  tran,
            'postDate':         post,
            'subClass':         transaction['subClass']['title'] if transaction.get('subClass') else None
            #'subClass_code': transaction['subClass']['code'] if transaction.get('subClass') else None
        }
        transactions.append(transaction)
    #transaction_df['day']
    transaction_df = pd.DataFrame(transactions)

    transaction_df['transactionDate'] = pd.to_datetime(transaction_df['transactionDate'],format="%Y-%m-%d")
    transaction_df['day']   = transaction_df['transactionDate'].dt.day      # Create new columns for day, month, and year
    transaction_df['month'] = transaction_df['transactionDate'].dt.month    # Create new columns for day, month, and year
    transaction_df['year']  = transaction_df['transactionDate'].dt.year     # Create new columns for day, month, and year
    #print(transaction_df)
    return transaction_df


def cache_transactions(tran_data):
    """
    Caches transaction data (from Dataframe format) for a Dolfin user.
    Inserts transaction data into the transactions table, including transaction ID, type, status, description, etc.\n
    NEW - Transaction data stored in a different database
    """
    try:
        with sqlite3.connect(transactions_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions
                (id VARCHAR(255) PRIMARY KEY,
                    type VARCHAR(50),
                    status VARCHAR(50),
                    description TEXT,
                    amount REAL,
                    account VARCHAR(255),
                    balance REAL,
                    direction VARCHAR(50),
                    class VARCHAR(50),
                    institution VARCHAR(50),
                    transactionDate TEXT,
                    postDate TEXT,
                    subClass VARCHAR(255),
                    day INTEGER,
                    month INTEGER,
                    year INTEGER);
            ''')
            #--subClass_code VARCHAR(50));
            insert_statement = '''
                INSERT INTO transactions (id, type, status, description, amount, account, balance, direction, class, institution, transactionDate, postDate, subClass, day, month, year) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''' #left out: #, subClass_code) -> made subClasstitle = Subclass
            for index, row in tran_data.iterrows():
                cursor.execute(insert_statement, (
                    row['id'], row['type'], row['status'], row['description'], 
                    row['amount'], row['account'], row['balance'], row['direction'], 
                    row['class'], row['institution'], str(row['transactionDate']), row['postDate'], 
                    row['subClass'], row['day'], row['month'], row['year'])) # left out: , row['subClass_code']

        return "CACHE - Transactions for user successfully inserted."

    except sqlite3.Error as e:
        return "CACHE - An error occurred: " + str(e)

# irrelevant with separate db
# def fetch_transactions_by_user(user_id):
#     """
#     Fetches cached transaction data based on the user ID.
#     Queries the transactions table for all transaction information for a specific user.
#     """
#     try:
#         with sqlite3.connect(transactions_db_path) as conn:
#             query = "SELECT * FROM transactions WHERE trans_u_id = ?"
#             return pd.read_sql_query(query, conn, params=(user_id,))
#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")


def clear_transactions():
    """
    Clears all cached data from the transactions table.
    Deletes all records from the transactions table.
    """
    try:
        # Database connection
        with sqlite3.connect(transactions_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions
                (id VARCHAR(255) PRIMARY KEY,
                    type VARCHAR(50),
                    status VARCHAR(50),
                    description TEXT,
                    amount REAL,
                    account VARCHAR(255),
                    balance REAL,
                    direction VARCHAR(50),
                    class VARCHAR(50),
                    institution VARCHAR(50),
                    transactionDate TEXT,
                    postDate TEXT,
                    subClass VARCHAR(255),
                    day INTEGER,
                    month INTEGER,
                    year INTEGER);
            ''')
            #Omitted due to different structure:
            #--subClass_code VARCHAR(50));
            #--trans_u_id INTEGER NOT NULL;
            #--FOREIGN KEY (trans_u_id) REFERENCES users (u_id) ON DELETE CASCADE ON UPDATE CASCADE);

            # SQL statement to delete all data from the transactions table
            cursor.execute("DELETE FROM transactions;")
            #print("Transactions table cleared successfully.")
        return "CLEAR DATABASE - Transactions cleared successfully."
    except sqlite3.Error as e:
        return "CLEAR DATABASE - An error occurred: " + str(e)
