import mysql.connector
from db import db

def get_all_exams():
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name, date FROM exams ORDER BY date ASC")
        exams = cursor.fetchall()

        return {
            "status": True,
            "exams": exams
        }

    except mysql.connector.Error as err:
        return {
            "status": False,
            "error": str(err),
            "exams": []
        }

    finally:
        connection.close()
