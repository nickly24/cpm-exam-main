import mysql.connector
from db import db

def get_directions():
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        database=db.db
    )
    
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM directions"
    cursor.execute(query)
    directions = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return directions