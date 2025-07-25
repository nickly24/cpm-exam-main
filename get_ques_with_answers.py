import mysql.connector
from db import db

def get_test_with_questions_and_answers(test_id):
    try:
        connection = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = connection.cursor(dictionary=True)

        # Получаем все вопросы теста
        cursor.execute("""
            SELECT q.id as question_id, q.question, q.type
            FROM test_questions q
            WHERE q.test_id = %s
        """, (test_id,))
        questions = cursor.fetchall()

        if not questions:
            return {
                "status": False,
                "message": "Вопросы не найдены"
            }

        # Получаем все ответы, сгруппированные по question_id
        question_ids = [q["question_id"] for q in questions]
        format_strings = ','.join(['%s'] * len(question_ids))

        cursor.execute(f"""
            SELECT a.id as answer_id, a.answer, a.status, a.questions_id
            FROM answers a
            WHERE a.questions_id IN ({format_strings})
        """, tuple(question_ids))
        answers = cursor.fetchall()

        # Группировка ответов по вопросам
        answers_by_question = {}
        for a in answers:
            qid = a["questions_id"]
            if qid not in answers_by_question:
                answers_by_question[qid] = []
            answers_by_question[qid].append({
                "answer_id": a["answer_id"],
                "answer": a["answer"],
                "status": a["status"]
            })

        # Формируем итоговую структуру
        result = []
        for q in questions:
            qid = q["question_id"]
            result.append({
                "question_id": qid,
                "question": q["question"],
                "type": q["type"],
                "answers": answers_by_question.get(qid, [])
            })

        return {
            "status": True,
            "test_id": test_id,
            "questions": result
        }

    except mysql.connector.Error as err:
        return {
            "status": False,
            "message": f"Ошибка: {err}"
        }
    finally:
        cursor.close()
        connection.close()