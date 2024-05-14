import sqlite3
from api.basiq_api import Core, Data
import os
from dotenv import load_dotenv
import json
import webbrowser
import pandas as pd

# Load environment variables from a .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
api_key = API_KEY
core_instance = Core(api_key)
data_instance = Data()
access_token = core_instance.generate_auth_token()
database_address = "../db/dolfin_db.db"


def init_dolfin_db():
    """
    Initializes the database by creating the 'users' and 'transactions' tables if they don't already exist.
    Sets up foreign key constraints as well.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users
                (u_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email VARCHAR(255),
                 mobile VARCHAR(255),
                 first_name VARCHAR(255),
                 middle_name VARCHAR(255),
                 last_name VARCHAR(255),
                 password VARCHAR(255),
                 basiq_id VARCHAR(255) DEFAULT NULL,
                 gender VARCHAR(50),
                 occupation VARCHAR(255),
                 birth TEXT,
                 address VARCHAR(255),
                 city VARCHAR(255),
                 country VARCHAR(255),
                 state VARCHAR(255),
                 postcode VARCHAR(255));
            ''')
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
                             postDate TIMESTAMP,
                             subClass_title VARCHAR(255),
                             subClass_code VARCHAR(50),
                             trans_u_id INTEGER NOT NULL,
                             FOREIGN KEY (trans_u_id) REFERENCES users (u_id) ON DELETE CASCADE ON UPDATE CASCADE);
                        ''')
            return "Managed to init dolfin_db."
    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def register_user(email, mobile, first_name, middle_name, last_name, password, gender, occupation, birth, address, city,
                  country, state, postcode):
    """
    Registers a new user in the database.
    Parameters include personal information, credentials of the user, and address details.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users (email, mobile, first_name, middle_name, last_name, password, gender, occupation, birth, address, city, country, state, postcode)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (email, mobile, first_name, middle_name, last_name, password, gender, occupation, birth,
                            address, city, country, state, postcode))
            conn.commit()
            return "User inserted successfully into 'users' table."
    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def get_basiq_id(user_id):
    """
    Retrieves the Basiq ID for a given user from the database.

    Parameters:
    - user_id: The unique identifier of the user whose Basiq ID is being requested.

    Returns:
    - The Basiq ID of the user if found, otherwise a message indicating no user was found.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT basiq_id FROM users WHERE u_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return "No user found with the given ID."
    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def get_user_info(user_id):
    """
    Fetches and returns basic information about a user given their user ID.

    Parameters:
    - user_id: The unique identifier of the user.

    Returns:
    - A dictionary containing the email, mobile, first name, middle name, and last name of the user if found,
      otherwise a message indicating no user was found.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email, mobile, first_name, middle_name, last_name FROM users WHERE u_id = ?",
                           (user_id,))
            result = cursor.fetchone()
            if result:
                user_info = {
                    "email": result[0],
                    "mobile": result[1],
                    "firstName": result[2],
                    "middleName": result[3],
                    "lastName": result[4]
                }
                return user_info
            else:
                return "No user found with the given ID."
    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def register_basiq_id(user_id):
    """
    Updates the user's record in the database with a new Basiq ID obtained from the Basiq API.

    Parameters:
    - user_id: The unique identifier of the user whose Basiq ID is to be updated.

    Returns:
    - A success message if the Basiq ID was updated successfully,
      otherwise a message indicating no user was found or an error occurred.
    """
    try:
        new_basiq_id = json.loads(core_instance.create_user_by_dict(get_user_info(user_id), access_token)).get('id')
        with sqlite3.connect(database_address) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET basiq_id = ? WHERE u_id = ?", (new_basiq_id, user_id))
            if cursor.rowcount == 0:
                return "No user found with the given ID."
            conn.commit()
            return "basiq_id updated successfully for user ID {}".format(user_id)
    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def link_bank_account(user_id):
    """
    Opens a web browser for the user to link their bank account via the Basiq API.

    Parameters:
    - user_id: The unique identifier of the user who is linking their bank account.

    Returns:
    - Opens a web browser to the bank account linking page if the user is found and has a basiq_id.
      Otherwise, returns a message indicating no user was found or an error occurred.
    """

    try:
        with sqlite3.connect(database_address) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT basiq_id FROM users WHERE u_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                link = json.loads(core_instance.create_auth_link(result[0], access_token)).get('links').get('public')
                webbrowser.open(link)
            else:
                return "No user found with the given ID."
    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def request_transactions(user_id):
    """
    Fetches transaction data for a given user from the Basiq API and returns it as a DataFrame.

    Parameters:
    - user_id: The unique identifier of the user whose transactions are being requested.

    Returns:
    - A DataFrame containing the transaction data for the user.
    """
    tran_data = json.loads(data_instance.get_transactions(get_basiq_id(user_id), access_token))
    transaction_list = tran_data['data']
    transactions = []
    for transaction in transaction_list:
        # Add try-except block to handle missing 'id' key
        try:
            transaction_data = {
                'type': transaction['type'],
                'id': transaction['id'],
                'status': transaction['status'],
                'description': transaction['description'],
                'amount': transaction['amount'],
                'account': transaction['account'],
                'balance': transaction['balance'],
                'direction': transaction['direction'],
                'class': transaction['class'],
                'institution': transaction['institution'],
                'postDate': transaction['postDate'],
                'subClass_title': transaction['subClass']['title'] if transaction.get('subClass') else None,
                'subClass_code': transaction['subClass']['code'] if transaction.get('subClass') else None
            }
            transactions.append(transaction_data)
        except KeyError as e:
            # Handle the case where 'id' key is missing
            print(f"Skipping transaction: {e}")
    transaction_df = pd.DataFrame(transactions)
    return transaction_df


def cache_transactions(user_id, tran_data):
    """
    Inserts transaction data for a user into the database.

    Parameters:
    - user_id: The unique identifier of the user whose transactions are being cached.
    - tran_data: A DataFrame containing the transaction data to be cached.

    Returns:
    - A message indicating the transactions were successfully inserted, or an error message if an error occurred.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            insert_statement = '''
                INSERT INTO transactions (id, type, status, description, amount, account, balance, direction, class, institution, postDate, subClass_title, subClass_code, trans_u_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            for index, row in tran_data.iterrows():
                cursor.execute(insert_statement, (
                    row['id'], row['type'], row['status'], row['description'], row['amount'],
                    row['account'], row['balance'], row['direction'], row['class'], row['institution'],
                    row['postDate'], row['subClass_title'], row['subClass_code'], user_id))

        return "Transactions successfully inserted."

    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def fetch_transactions_by_user(user_id):
    """
    Fetches all transactions from the database for a given user.

    Parameters:
    - user_id: The unique identifier of the user whose transactions are being fetched.

    Returns:
    - A DataFrame containing all the transactions for the user, or prints an error message if an error occurred.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            query = "SELECT * FROM transactions WHERE trans_u_id = ?"
            return pd.read_sql_query(query, conn, params=(user_id,))
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def clear_transactions(user_id):
    """
    Clears all transactions from the database for a given user.

    Parameters:
    - user_id: The unique identifier of the user whose transactions are being cleared.

    Returns:
    - A message indicating the transactions for the user were successfully cleared, or an error message if an error occurred.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE trans_u_id = ?;", (user_id,))
        return "Transactions for user {} cleared successfully.".format(user_id)
    except sqlite3.Error as e:
        return "An error occurred: " + str(e)


def verify_user(email, provided_password):
    """
    Verifies a user's email and password.
    If the password matches the one in the database, returns the user's ID.
    Assumes passwords are stored in a hashed format.

    :param email: The user's email address.
    :param provided_password: The password to verify.
    :return: The user's ID if the email and password match, None otherwise.
    """
    try:
        with sqlite3.connect(database_address) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT u_id, password FROM users WHERE email = ?''', (email,))
            user_record = cursor.fetchone()
            if user_record:
                user_id, stored_password = user_record
                if provided_password == stored_password:
                    return user_id
            return None
    except sqlite3.Error as e:
        print("An error occurred:", e)
        return None
