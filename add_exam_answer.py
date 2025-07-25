from db import db
import mysql.connector

def add_exam_answer(exam_session_id, question_id, result):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor()

    try:
        insert_query = """
            INSERT INTO exams_answers (exam_session_id, question_id, result)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (exam_session_id, question_id, result))
        connection.commit()

        return {"status": True, "message": "Ответ успешно добавлен"}

    except mysql.connector.Error as err:
        return {"status": False, "message": str(err)}

    finally:
        cursor.close()
        connection.close()
