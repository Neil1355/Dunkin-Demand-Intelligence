import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # <-- replace with yours
        password="yourpassword",  
        database="dunkin_demand"
    )