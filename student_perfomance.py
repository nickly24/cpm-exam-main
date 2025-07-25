import mysql.connector
from db import db

def calculate_students_performance(date_start, date_end):
    try:
        conn = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = conn.cursor(dictionary=True)

        # Получаем всех студентов
        cursor.execute("SELECT id FROM students")
        students = cursor.fetchall()
        results = []

        for student in students:
            student_id = student['id']

            # 1. Баллы за домашки типа "ОВ"
            cursor.execute("""
                SELECT hs.result
                FROM homework_sessions hs
                JOIN homework h ON hs.homework_id = h.id
                WHERE hs.student_id = %s
                  AND h.type = 'ОВ'
                  AND h.deadline BETWEEN %s AND %s
            """, (student_id, date_start, date_end))
            ov_results = [r['result'] for r in cursor.fetchall() if r['result'] is not None]
            ov_score = (sum(ov_results) / len(ov_results) * 25) if ov_results else 0

            # 2. Баллы за экзамены
            cursor.execute("""
                SELECT es.result
                FROM exams_sessions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s
                  AND e.date BETWEEN %s AND %s
            """, (student_id, date_start, date_end))
            exam_results = [r['result'] for r in cursor.fetchall() if r['result'] is not None]
            exam_score = (sum(exam_results) / len(exam_results) * 30) if exam_results else 0

            # 3. Средние баллы по веткам (тесты)
            cursor.execute("""
                SELECT t.branch_id, ts.result
                FROM test_session ts
                JOIN tests t ON ts.test_id = t.id
                WHERE ts.student_id = %s
                  AND t.date BETWEEN %s AND %s
                  AND ts.result IS NOT NULL
            """, (student_id, date_start, date_end))
            rows = cursor.fetchall()

            branch_totals = {}
            branch_counts = {}

            for r in rows:
                branch_id = r['branch_id']
                result = r['result']
                if branch_id not in branch_totals:
                    branch_totals[branch_id] = 0
                    branch_counts[branch_id] = 0
                branch_totals[branch_id] += result
                branch_counts[branch_id] += 1

            branch_averages = [branch_totals[bid] / branch_counts[bid] for bid in branch_totals]
            branch_score = (sum(branch_averages) / len(branch_averages) * 45) if branch_averages else 0

            total = ov_score + exam_score + branch_score

            results.append({
                "student_id": student_id,
                "homework_ov_score": round(ov_score, 2),
                "exam_score": round(exam_score, 2),
                "branch_avg_score": round(branch_score, 2),
                "total_score": round(total, 2)
            })

        return results

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()