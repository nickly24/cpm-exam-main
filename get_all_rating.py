import mysql.connector
from db import db

def get_all_students_with_rating():
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
            SELECT s.id, s.full_name, r.rate, r.homework_rate, r.exam_rate, r.test_rate
            FROM students s
            LEFT JOIN rating r ON s.id = r.student_id
            ORDER BY r.rate DESC
        """)
        students = cursor.fetchall()

        return {"students": students}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()