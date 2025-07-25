import mysql.connector
from db import db

def get_tests_w_results(student_id):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        database=db.db
    )
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Запрос для получения всех тестов студента с информацией о ветках
        query = """
        SELECT 
            ts.id as session_id,
            ts.result,
            t.id as test_id,
            t.name as test_name,
            t.date as test_date,
            b.id as branch_id,
            b.name as branch_name
        FROM test_session ts
        JOIN tests t ON ts.test_id = t.id
        JOIN test_brancnhes b ON t.branch_id = b.id
        WHERE ts.student_id = %s
        ORDER BY b.name, t.date
        """
        
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        
        # Структурируем данные
        output = {}
        
        for row in results:
            branch_id = row['branch_id']
            
            if branch_id not in output:
                output[branch_id] = {
                    'branch_name': row['branch_name'],
                    'tests': []
                }
            
            output[branch_id]['tests'].append({
                'test_id': row['test_id'],
                'test_name': row['test_name'],
                'date': row['test_date'],
                'result': row['result'],
                'session_id': row['session_id']
            })
        
        return output
        
    finally:
        cursor.close()
        connection.close()