# get_random_question_by_exam_simple.py

import mysql.connector
import random
from db import db

def get_random_question_by_exam(exam_id):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM exams WHERE id = %s", (exam_id,))
        exam = cursor.fetchone()
        if not exam:
            return {"status": False, "error": "Экзамен не найден"}

        # Предполагается, что в таблице вопросов есть поле exam_id
        cursor.execute("""
            SELECT id, question, answer 
            FROM questions 
            WHERE exam_id = %s
        """, (exam_id,))
        questions = cursor.fetchall()

        if not questions:
            return {"status": False, "error": "Нет вопросов для этого экзамена"}

        question = random.choice(questions)

        return {
            "status": True,
            "question_id": question["id"],
            "question": question["question"],
            "answer": question["answer"]
        }

    except mysql.connector.Error as err:
        return {"status": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()
