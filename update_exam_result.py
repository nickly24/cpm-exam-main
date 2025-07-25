from db import db
import mysql.connector

def update_exam_result(exam_session_id, result):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor()

    try:
        update_query = """
            UPDATE exams_sessions
            SET result = %s
            WHERE id = %s
        """
        cursor.execute(update_query, (result, exam_session_id))
        connection.commit()

        return {"status": True, "message": "Оценка успешно обновлена"}

    except mysql.connector.Error as err:
        return {"status": False, "message": str(err)}

    finally:
        cursor.close()
        connection.close()
