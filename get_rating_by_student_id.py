import mysql.connector
from db import db

def get_rating_by_student_id(student_id):
    try:
        conn = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM rating
            WHERE student_id = %s
        """, (student_id,))
        result = cursor.fetchall()

        return result if result else {"message": f"No rating data found for student ID {student_id}"}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()