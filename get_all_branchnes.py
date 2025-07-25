import mysql.connector
from db import db

def get_all_test_branches():
    try:
        conn = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name FROM test_brancnhes")
        branches = cursor.fetchall()

        return branches

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()