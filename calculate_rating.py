import mysql.connector
from db import db
from datetime import datetime

def fill_rating_table_by_period():
    try:
        conn = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = conn.cursor(dictionary=True)

        # Определяем текущую дату и семестровый диапазон
        today = datetime.today()
        year = today.year

        if today.month >= 1 and today.month <= 7:
            # Второй семестр: 1 января — 15 июля
            start_date = f"{year}-01-01"
            end_date = f"{year}-07-15"
        else:
            # Первый семестр: 1 сентября — 31 декабря
            start_date = f"{year}-09-01"
            end_date = f"{year}-12-31"

        # Получаем экзамены, тесты, ветки
        cursor.execute("SELECT id FROM exams WHERE date BETWEEN %s AND %s", (start_date, end_date))
        exam_ids = [row['id'] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM tests WHERE date BETWEEN %s AND %s", (start_date, end_date))
        test_ids = [row['id'] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM test_brancnhes")
        branch_ids = [row['id'] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM students")
        students = cursor.fetchall()

        for student in students:
            student_id = student['id']

            # Домашки типа 'ОВ'
            cursor.execute("""
                SELECT AVG(result) as avg_homework
                FROM homework_sessions
                WHERE student_id = %s AND homework_id IN (
                    SELECT id FROM homework WHERE type = 'ОВ' AND deadline BETWEEN %s AND %s
                )
            """, (student_id, start_date, end_date))
            hw = cursor.fetchone()
            homework_rate = round(hw['avg_homework'], 2) if hw and hw['avg_homework'] else 0

            # Экзамены
            exam_rate = 0
            if exam_ids:
                format_strings = ','.join(['%s'] * len(exam_ids))
                cursor.execute(f"""
                    SELECT AVG(result) as avg_exam
                    FROM exams_sessions
                    WHERE student_id = %s AND exam_id IN ({format_strings})
                """, [student_id] + exam_ids)
                row = cursor.fetchone()
                exam_rate = round(row['avg_exam'], 2) if row and row['avg_exam'] else 0

            # Тесты по веткам
            total_branch_score = 0
            for branch_id in branch_ids:
                cursor.execute("""
                    SELECT AVG(result) as avg_test
                    FROM test_session
                    WHERE student_id = %s AND test_id IN (
                        SELECT id FROM tests
                        WHERE branch_id = %s AND date BETWEEN %s AND %s
                    )
                """, (student_id, branch_id, start_date, end_date))
                res = cursor.fetchone()
                total_branch_score += res['avg_test'] if res and res['avg_test'] else 0

            test_rate = round(total_branch_score / len(branch_ids), 2) if branch_ids else 0

            # Финальный рейтинг
            rate = round(float(homework_rate) * 0.25 + float(exam_rate) * 0.30 + float(test_rate) * 0.45, 2)

            # Обновляем или вставляем
            cursor.execute("""
                UPDATE rating
                SET homework_rate = %s, exam_rate = %s, test_rate = %s, rate = %s
                WHERE student_id = %s
            """, (homework_rate, exam_rate, test_rate, rate, student_id))

            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO rating (student_id, homework_rate, exam_rate, test_rate, rate)
                    VALUES (%s, %s, %s, %s, %s)
                """, (student_id, homework_rate, exam_rate, test_rate, rate))

        conn.commit()
        return {
            "message": "Rating table updated",
            "period": f"{start_date} — {end_date}"
        }

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()