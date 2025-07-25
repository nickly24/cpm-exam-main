import mysql.connector
from db import db

def get_student_tests_grouped_by_branch(student_id):
    try:
        connection = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = connection.cursor(dictionary=True)

        # Получаем все сданные тесты с баллами
        cursor.execute("""
            SELECT test_id, result
            FROM test_session
            WHERE student_id = %s
        """, (student_id,))
        passed_tests_raw = cursor.fetchall()
        passed_tests = {row["test_id"]: row["result"] for row in passed_tests_raw}

        # Получаем все тесты с их ветками
        cursor.execute("""
            SELECT 
                t.id AS test_id,
                t.name AS test_name,
                t.branch_id,
                b.name AS branch_name
            FROM tests t
            LEFT JOIN test_brancnhes b ON t.branch_id = b.id
        """)
        all_tests = cursor.fetchall()

        # Группировка по ветке
        result = {}
        for test in all_tests:
            branch_key = test["branch_name"] or "Без категории"
            if branch_key not in result:
                result[branch_key] = []

            test_id = test["test_id"]
            is_passed = test_id in passed_tests

            test_info = {
                "test_id": test_id,
                "test_name": test["test_name"],
                "branch_id": test["branch_id"],
                "branch_name": test["branch_name"] or "Без категории",
                "status": "сдан" if is_passed else "не сдан"
            }

            if is_passed:
                test_info["score"] = passed_tests[test_id]

            result[branch_key].append(test_info)

        return {
            "status": True,
            "tests_by_branch": result
        }

    except mysql.connector.Error as err:
        return {
            "status": False,
            "message": f"Ошибка: {err}"
        }

    finally:
        cursor.close()
        connection.close()