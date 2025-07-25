import mysql.connector
from db import db

def create_test_with_questions_and_answers(test_data):
    try:
        conn = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = conn.cursor()

        # 1. Добавляем тест в таблицу tests
        cursor.execute("""
            INSERT INTO tests (name, branch_id, date)
            VALUES (%s, %s, %s)
        """, (test_data['name'], test_data['branch_id'], test_data['date']))
        test_id = cursor.lastrowid

        # 2. Добавляем вопросы в таблицу test_questions
        for question in test_data['questions']:
            cursor.execute("""
                INSERT INTO test_questions (question, type, test_id)
                VALUES (%s, %s, %s)
            """, (question['question_text'], question['type'], test_id))
            question_id = cursor.lastrowid

            # 3. Добавляем ответы в таблицу answers
            correct_answers = question['correct_answers']
            for answer_text in question['answers']:
                status = 1 if answer_text in correct_answers else 0
                cursor.execute("""
                    INSERT INTO answers (answer, status, questions_id)
                    VALUES (%s, %s, %s)
                """, (answer_text, status, question_id))

        conn.commit()
        return {"message": "Test created successfully", "test_id": test_id}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()