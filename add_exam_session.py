from db import db
import mysql.connector

def create_exam_session(student_id, exam_id):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        database=db.db
    )
    cursor = connection.cursor()

    # создаём запись в exams_sessions
    insert_query = """
        INSERT INTO exams_sessions (student_id, exam_id, result)
        VALUES (%s, %s, 0)
    """
    cursor.execute(insert_query, (student_id, exam_id))
    connection.commit()

    # получаем id новой сессии
    session_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Экзаменационная сессия создана успешно",
        "session_id": session_id,
        "student_id": student_id,
        "exam_id": exam_id
    }
