import mysql.connector  ## raw MySQL driver for direct queries and inserts
from sqlalchemy import create_engine  ## SQLAlchemy for pandas-compatible connections
import os  ## access environment variables for credentials

def get_connection():
    ## builds a raw MySQL connection using environment variables
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),      ## database server location
        user=os.getenv("DB_USER", "root"),           ## database username
        password=os.getenv("DB_PASSWORD", ""),       ## database password
        database=os.getenv("DB_NAME", "oee_optimizer")  ## target database
    )

def get_engine():
    ## reads credentials from environment variables
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    database = os.getenv("DB_NAME", "oee_optimizer")
    ## builds a SQLAlchemy engine using a connection string URL
    ## mysql+mysqlconnector tells SQLAlchemy which driver to use
    return create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

if __name__ == "__main__":
    conn = get_connection()  ## test raw connection
    print("Connected to MySQL:", conn.is_connected())  ## confirm connection
    conn.close()  ## always close after use