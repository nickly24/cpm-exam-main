import mysql.connector
from db import db

def create_test_session(test_id, student_id, result):
    try:
        connection = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO test_session (test_id, student_id, result)
            VALUES (%s, %s, %s)
        """, (test_id, student_id, result))

        connection.commit()

        return {
            "status": True,
            "message": "Сессия успешно создана"
        }

    except mysql.connector.Error as err:
        return {
            "status": False,
            "message": f"Ошибка при создании сессии: {err}"
        }

    finally:
        cursor.close()
        connection.close()