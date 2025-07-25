import mysql.connector
from db import db

def get_exams_w_results(student_id):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        database=db.db
    )
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Получаем все экзаменационные сессии студента с информацией об экзаменах
        query = """
        SELECT es.id as session_id, es.result as session_result, 
               e.id as exam_id, e.name as exam_name, e.date as exam_date
        FROM exams_sessions es
        JOIN exams e ON es.exam_id = e.id
        WHERE es.student_id = %s
        """
        cursor.execute(query, (student_id,))
        exam_sessions = cursor.fetchall()
        
        result = []
        
        for session in exam_sessions:
            # Для каждой сессии получаем вопросы и ответы
            query = """
            SELECT ea.id as answer_id, ea.result as answer_result,
                   q.id as question_id, q.question as question_text, q.answer as correct_answer
            FROM exams_answers ea
            JOIN questions q ON ea.question_id = q.id
            WHERE ea.exam_session_id = %s
            """
            cursor.execute(query, (session['session_id'],))
            questions = cursor.fetchall()
            
            # Формируем структуру данных для одной экзаменационной сессии
            exam_data = {
                'exam_id': session['exam_id'],
                'exam_name': session['exam_name'],
                'exam_date': session['exam_date'].strftime('%Y-%m-%d') if session['exam_date'] else None,
                'session_result': session['session_result'],
                'questions': [
                    {
                        'question_id': q['question_id'],
                        'question_text': q['question_text'],
                        'correct_answer': q['correct_answer'],
                        'student_answer_result': q['answer_result']
                    } for q in questions
                ]
            }
            
            result.append(exam_data)
        
        return result
        
    finally:
        cursor.close()
        connection.close()