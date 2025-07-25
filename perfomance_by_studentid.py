import mysql.connector
from db import db

def get_student_study_summary(student_id):
    try:
        conn = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = conn.cursor(dictionary=True)

        result = {}

        # Домашние задания
        cursor.execute("SELECT COUNT(*) AS total FROM homework")
        total_homework = cursor.fetchone()['total']

        cursor.execute("""
            SELECT COUNT(*) AS completed
            FROM homework_sessions
            WHERE student_id = %s AND date_pass IS NOT NULL
        """, (student_id,))
        completed_homework = cursor.fetchone()['completed']

        result['homework'] = {
            "completed": completed_homework,
            "total": total_homework
        }

        # Контрольные (экзамены)
        cursor.execute("SELECT COUNT(*) AS total FROM exams")
        total_exams = cursor.fetchone()['total']

        cursor.execute("""
            SELECT COUNT(*) AS completed, AVG(result) AS average_score
            FROM exams_sessions
            WHERE student_id = %s
        """, (student_id,))
        exam_row = cursor.fetchone()

        result['control_works'] = {
            "completed": exam_row['completed'],
            "total": total_exams,
            "average_score": round(exam_row['average_score'], 2) if exam_row['average_score'] else 0
        }

        # Тесты
        cursor.execute("SELECT COUNT(*) AS total FROM tests")
        total_tests = cursor.fetchone()['total']

        cursor.execute("""
            SELECT COUNT(*) AS completed, AVG(result) AS average_score
            FROM test_session
            WHERE student_id = %s
        """, (student_id,))
        test_row = cursor.fetchone()

        result['tests'] = {
            "completed": test_row['completed'],
            "total": total_tests,
            "average_score": round(test_row['average_score'], 2) if test_row['average_score'] else 0
        }

        # Посещаемость
        cursor.execute("""
            SELECT COUNT(*) AS count FROM attendance
            WHERE student_id = %s
        """, (student_id,))
        attendance_count = cursor.fetchone()['count']
        result['attendance'] = attendance_count

        return result

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()