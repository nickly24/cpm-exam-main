import mysql.connector
from db import db

def create_exam_with_questions(exam_data):
    try:
        conn = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = conn.cursor()

        # 1. Добавляем экзамен
        cursor.execute("""
            INSERT INTO exams (name, date)
            VALUES (%s, %s)
        """, (exam_data['name'], exam_data['date']))
        exam_id = cursor.lastrowid

        # 2. Добавляем вопросы
        for question in exam_data['questions']:
            cursor.execute("""
                INSERT INTO questions (question, answer, exam_id)
                VALUES (%s, %s, %s)
            """, (question['question_text'], question['correct_answer'], exam_id))

        conn.commit()
        return {"message": "Exam created successfully", "exam_id": exam_id}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()