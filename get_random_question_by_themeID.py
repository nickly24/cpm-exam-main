import mysql.connector
import random
from db import db

def get_random_question_by_theme(theme_id):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor(dictionary=True)

    try:
        # Проверяем, существует ли тема
        cursor.execute("SELECT id FROM themes WHERE id = %s", (theme_id,))
        theme = cursor.fetchone()
        if not theme:
            return {"status": False, "error": "Тема не найдена"}

        # Получаем все вопросы по теме
        cursor.execute("SELECT id, question, answer FROM questions WHERE theme_id = %s", (theme_id,))
        questions = cursor.fetchall()

        if not questions:
            return {"status": False, "error": "Нет вопросов по данной теме"}

        # Выбираем случайный вопрос
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
        connection.close()
        cursor.close()