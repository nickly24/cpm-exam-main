from db import db
import mysql.connector

def get_all_exam_sessions():
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        database=db.db
    )
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT 
            es.id AS session_id,
            s.full_name AS student_name,
            s.id AS student_id,
            e.name AS exam_name,
            e.date AS exam_date,
            es.result AS session_result,
            ea.question_id,
            ea.result AS question_score
        FROM exams_sessions es
        JOIN students s ON es.student_id = s.id
        JOIN exams e ON es.exam_id = e.id
        LEFT JOIN exams_answers ea ON ea.exam_session_id = es.id
        ORDER BY es.id, ea.id;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    sessions = {}

    for row in rows:
        sid = row['session_id']
        if sid not in sessions:
            sessions[sid] = {
                'student_id': row['student_id'],
                'student_name': row['student_name'],
                'exam_name': row['exam_name'],
                'exam_date': str(row['exam_date']),
                'session_result': row['session_result'],
                'answers': [],
                'grade': None  # оценка будет позже
            }
        sessions[sid]['answers'].append({
            'question_id': row['question_id'],
            'question_score': row['question_score']
        })

    # теперь добавим оценки
    for session in sessions.values():
        scores = [ans['question_score'] for ans in session['answers'] if ans['question_score'] is not None]
        total = sum(scores)

        if total.is_integer():
            if total == 6:
                session['grade'] = "Оценка: 5"
            elif total == 5:
                session['grade'] = "Оценка: 4"
            elif total == 4:
                session['grade'] = "Оценка: 3 "
            else:
                session['grade'] = "Оценка: неудовлетворительно"
        else:
            # округление
            floor = int(total)
            diff = total - floor
            if diff == 0.5:
                session['grade'] = "требуется дополнительный вопрос (порог между {} и {})".format(
                    _interpret_grade(floor), _interpret_grade(floor + 1)
                )

    cursor.close()
    connection.close()
    return sessions

def _interpret_grade(score):
    if score == 6:
        return "отлично"
    elif score == 5:
        return "хорошо"
    elif score == 4:
        return "удовлетворительно"
    else:
        return "неудовлетворительно"
