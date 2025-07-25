import mysql.connector
from db import db

def get_question_by_id(question_id):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, question, answer FROM questions WHERE id = %s", (question_id,))
        question = cursor.fetchone()


        if not question:
            return {"status": False, "error": "Question not found"}

        return {"status": True, "res": question}

    except mysql.connector.Error as err:
        print(f"Ошибка базы данных: {err}")
        return {"status": False, "error": str(err)}

    finally:
        connection.close()

# === ПРИМЕР ===
if __name__ == "__main__":
    response = get_question_by_id(1)
    print(response)
