import mysql.connector
from db import db

def get_all_themes():
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name FROM themes ORDER BY id ASC")
        themes = cursor.fetchall()

        return {
            "status": True,
            "themes": themes
        }

    except mysql.connector.Error as err:
        return {
            "status": False,
            "error": str(err),
            "themes": []
        }

    finally:
        connection.close()
