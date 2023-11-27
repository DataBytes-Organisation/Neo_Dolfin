from dotenv import load_dotenv
import os 
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

load_dotenv()  # Load environment variables from .env

# Access environment variables
PASSWORD = os.getenv("PASSWORD")
PUBLIC_IP = os.getenv("PUBLIC_IP_ADDRESS")
DBNAME = os.getenv("DBNAME")
PROJECT_ID = os.getenv("PROJECT_ID")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:australia-southeast2-c:{PROJECT_ID}"
DB_USER = 'root'
DB_PASS = PASSWORD
DB_NAME = DBNAME

# initialize Connector object
connector = Connector()

# function to return the database connection object
def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn

# create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

# connect to connection pool
with pool.connect() as db_conn:
    # create ratings table in our sandwiches database
    db_conn.execute(
        sqlalchemy.text(
            "CREATE TABLE IF NOT EXISTS user "
            "( id SERIAL NOT NULL, username VARCHAR(80) UNIQUE NOT NULL, "
            "email VARCHAR(80) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, "
            "PRIMARY KEY (id));"
        )
    )

    # commit transaction (SQLAlchemy v2.X.X is commit as you go)
    db_conn.commit()

    # insert data into our ratings table
    insert_stmt = sqlalchemy.text(
        "INSERT INTO user (id, username, email, password) VALUES (:name, :username, :email, :password)",
    )

    # insert entries into table
    db_conn.execute(insert_stmt, parameters={"id": "1", "name": "Wentworth", "username": "Wentwork", "email":"wentworth@gmail.com", "password":"whislter"})
    db_conn.execute(insert_stmt, parameters={"id": "2", "name": "Whistler", "username": "Whistler", "email":"whistler@gmail.com", "password":"ShowBox"})
    db_conn.execute(insert_stmt, parameters={"id": "3", "name": "Gilfoyle", "username": "Gilfoyle", "email":"gilfoyle@gmail.com", "password":"PiedPiper"})
    db_conn.execute(insert_stmt, parameters={"id": "4", "name": "gavinBelson", "username": "gavinBelson", "email":"gavinb@gmail.com", "password":"hooli2016"})
    db_conn.execute(insert_stmt, parameters={"id": "5", "name": "richard", "username": "richard", "email":"richard@gmail.com", "password":"tabsnotspaces"})
    db_conn.execute(insert_stmt, parameters={"id": "6", "name": "jared", "username": "jared", "email":"jared@gmail.com", "password":"django"})
    db_conn.execute(insert_stmt, parameters={"id": "7", "name": "tester", "username": "tester", "email":"tester@gmail.com", "password":"tester001"})

    # commit transactions
    db_conn.commit()

    # query and fetch ratings table
    results = db_conn.execute(sqlalchemy.text("SELECT * FROM ratings")).fetchall()

    # show results
    for row in results:
        print(row)