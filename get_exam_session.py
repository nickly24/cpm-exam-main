import mysql.connector
from db import db

def get_exam_session_by_student_and_exam(student_id, exam_id):
    try:
        connection = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = connection.cursor(dictionary=True, buffered=True)

        # Получаем сессию
        cursor.execute("""
            SELECT * FROM exams_sessions 
            WHERE student_id = %s AND exam_id = %s
        """, (student_id, exam_id))
        session = cursor.fetchone()

        if not session:
            return {"status": False, "error": "Сессия не найдена"}

        session_id = session["id"]

        # Получаем все вопросы и ответы по этой сессии
        cursor.execute("""
            SELECT 
                q.id AS question_id,
                q.question,
                q.answer AS correct_answer,
                ea.result
            FROM exams_answers ea
            JOIN questions q ON ea.question_id = q.id
            WHERE ea.exam_session_id = %s
        """, (session_id,))
        answers = cursor.fetchall()

        # Преобразование результата оценки в текстовую форму
        numeric_result = session.get("result")
        grade = None
        if numeric_result is not None:
            if numeric_result >= 5:
                grade = "отлично"
            elif numeric_result >= 4:
                grade = "хорошо"
            elif numeric_result >= 3:
                grade = "удовлетворительно"
            else:
                grade = "неудовлетворительно"

        return {
            "status": True,
            "session": session,
            "score": numeric_result,
            "grade": grade,
            "answers": answers
        }

    except mysql.connector.Error as err:
        return {"status": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()
