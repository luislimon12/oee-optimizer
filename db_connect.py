import mysql.connector
import os
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "oee_optimizer")
    )



if __name__ == "__main__":
    conn = get_connection()
    print("Connected to MySQL:", conn.is_connected())
    conn.close()