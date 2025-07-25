import mysql.connector
from db import db

def get_student_name_and_class(student_id):
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
            SELECT full_name, class
            FROM students
            WHERE id = %s
        """, (student_id,))
        result = cursor.fetchone()

        if result:
            return {"id": student_id, "name": result['full_name'], "class": result['class']}
        else:
            return {"error": f"Student with ID {student_id} not found."}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()