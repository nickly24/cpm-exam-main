from db import db
from flask import Flask, jsonify, request
from flask_cors import CORS
from jwt_auth import require_auth, require_role, require_self_or_role
from datetime import datetime
from get_directions import get_directions
from get_tests_by_direction import get_tests_by_direction
from create_test import create_test, update_test, delete_test, get_test_by_id
from create_test_session import create_test_session, get_test_session_by_id, get_test_sessions_by_student, get_test_sessions_by_test, get_test_session_stats, get_test_session_by_student_and_test, recalc_test_sessions
from get_student_attendance import get_student_attendance
from get_exams import get_all_exams, get_exam_session, get_exam_sessions_by_student, get_all_exam_sessions, get_exam_sessions_by_exam
from get_external_tests import get_external_tests_with_results_by_student, get_all_external_tests_by_direction_for_admin
from save_ratings import save_all_ratings
from db_pool import get_db_connection, close_db_connection
from pymongo import MongoClient 




app = Flask(__name__)
CORS(app, resources={
    r"/*": {  # Обратите внимание на "/*" вместо "/api/*"
        "origins": [
            "https://cpm-lms.ru",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ],  # Только разрешенные домены
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,  # Важно для работы с cookies
        "expose_headers": ["Content-Type"]
    }
})


@app.route("/directions")
def get_directions_route():
    directions = get_directions()
    return jsonify(directions)

@app.route("/tests/<direction>")
@require_auth
def get_tests_by_direction_route(direction, current_user=None):
    """
    Получает все тесты по направлению (включая внешние тесты)
    direction - название направления
    """
    # Получаем обычные тесты из MongoDB
    tests = get_tests_by_direction(direction)
    
    # Получаем ID направления по названию
    directions = get_directions()
    direction_obj = next((d for d in directions if d['name'] == direction), None)
    
    if direction_obj:
        direction_id = direction_obj['id']
        student_id = current_user.get('id') if current_user else None
        
        try:
            # Получаем внешние тесты
            if student_id and current_user.get('role') == 'student':
                # Для студентов получаем тесты с результатами
                # Убеждаемся, что student_id - int
                student_id = int(student_id) if student_id else None
                external_tests = get_external_tests_with_results_by_student(direction_id, student_id)
            else:
                # Для админов и других ролей получаем все внешние тесты
                external_tests = get_all_external_tests_by_direction_for_admin(direction_id)
            
            # Объединяем обычные и внешние тесты
            all_tests = tests + external_tests
        except Exception as e:
            # Если ошибка при получении внешних тестов, возвращаем только обычные
            print(f"Ошибка при получении внешних тестов: {str(e)}")
            all_tests = tests
    else:
        all_tests = tests
    
    return jsonify(all_tests)

@app.route("/test/<test_id>")
@require_auth
def get_test_by_id_route(test_id, current_user=None):
    test = get_test_by_id(test_id)
    if test:
        return jsonify(test)
    return jsonify({"error": "Test not found"}), 404

@app.route("/create-test", methods=["POST"])
@require_role('admin')
def create_test_route(current_user=None):
    test_data = request.get_json()
    test_id = create_test(test_data)
    return jsonify({"id": test_id})

@app.route("/test/<test_id>", methods=["PUT"])
@require_role('admin')
def update_test_route(test_id, current_user=None):
    test_data = request.get_json()
    
    # Проверяем, существует ли тест
    existing_test = get_test_by_id(test_id)
    if not existing_test:
        return jsonify({"error": "Test not found"}), 404
    
    # Обновляем тест
    success = update_test(test_id, test_data)
    
    if success:
        # Пересчитываем все сессии по этому тесту
        recalc_stats = recalc_test_sessions(test_id)
        return jsonify({
            "message": "Test updated successfully",
            "testId": test_id,
            "recalc": recalc_stats
        })
    else:
        return jsonify({"error": "Failed to update test"}), 500

@app.route("/test/<test_id>", methods=["DELETE"])
@require_role('admin')
def delete_test_route(test_id, current_user=None):
    # Проверяем, существует ли тест
    existing_test = get_test_by_id(test_id)
    if not existing_test:
        return jsonify({"error": "Test not found"}), 404
    
    # Удаляем тест и все связанные сессии
    result = delete_test(test_id)
    
    return jsonify({
        "message": "Test and related sessions deleted successfully",
        "testId": test_id,
        "deletedSessions": result["sessions_deleted"],
        "totalDeleted": result["total_deleted"]
    })

@app.route("/create-test-session", methods=["POST"])
@require_self_or_role('studentId', 'admin')
def create_test_session_route(current_user=None):
    session_data = request.get_json()
    
    # Проверяем обязательные поля
    required_fields = ["studentId", "testId", "testTitle", "answers"]
    for field in required_fields:
        if field not in session_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    result = create_test_session(
        student_id=session_data["studentId"],
        test_id=session_data["testId"],
        test_title=session_data["testTitle"],
        answers=session_data["answers"],
        score=session_data.get("score"),
        time_spent_minutes=session_data.get("timeSpentMinutes")
    )
    
    # Если тест уже сдан, возвращаем ошибку
    if not result["success"]:
        return jsonify({
            "error": result["error"],
            "message": result["message"],
            "existingSessionId": result.get("existingSessionId"),
            "existingScore": result.get("existingScore"),
            "completedAt": result.get("completedAt")
        }), 409  # Conflict status code
    
    # Если успешно создана, возвращаем ID сессии
    return jsonify({"id": result["sessionId"]})

@app.route("/test-session/<session_id>")
@require_auth
def get_test_session_route(session_id, current_user=None):
    # Нужно проверить, что сессия принадлежит пользователю или он админ
    session = get_test_session_by_id(session_id)
    if not session:
        return jsonify({"error": "Test session not found"}), 404
    
    # Проверяем доступ: либо это сессия студента, либо админ
    if current_user.get('role') != 'admin' and str(session.get('studentId')) != str(current_user.get('id')):
        return jsonify({
            'status': False,
            'error': 'Недостаточно прав доступа'
        }), 403
    
    return jsonify(session)

@app.route("/test-sessions/student/<student_id>")
@require_self_or_role('student_id', 'admin')
def get_test_sessions_by_student_route(student_id, current_user=None):
    sessions = get_test_sessions_by_student(student_id)
    return jsonify(sessions)

@app.route("/test-sessions/test/<test_id>")
@require_role('admin')
def get_test_sessions_by_test_route(test_id, current_user=None):
    sessions = get_test_sessions_by_test(test_id)
    return jsonify(sessions)

@app.route("/test-session/<session_id>/stats")
@require_auth
def get_test_session_stats_route(session_id, current_user=None):
    # Проверяем доступ к сессии
    session = get_test_session_by_id(session_id)
    if not session:
        return jsonify({"error": "Test session not found"}), 404
    
    # Проверяем доступ: либо это сессия студента, либо админ
    if current_user.get('role') != 'admin' and str(session.get('studentId')) != str(current_user.get('id')):
        return jsonify({
            'status': False,
            'error': 'Недостаточно прав доступа'
        }), 403
    
    stats = get_test_session_stats(session_id)
    if stats:
        return jsonify(stats)
    return jsonify({"error": "Test session not found"}), 404

@app.route("/test-session/student/<student_id>/test/<test_id>")
@require_self_or_role('student_id', 'admin')
def get_test_session_by_student_and_test_route(student_id, test_id, current_user=None):
    session = get_test_session_by_student_and_test(student_id, test_id)
    if session:
        return jsonify(session)
    return jsonify({"error": "Test session not found"}), 404


@app.route("/get-attendance", methods=["POST"])
@require_self_or_role('student_id', 'admin')
def get_attendance_route(current_user=None):
    """
    Получает посещаемость студента за определенный месяц
    Ожидает JSON: {"student_id": "123", "year_month": "2025-01"}
    """
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        year_month = data.get('year_month')
        
        if not student_id or not year_month:
            return jsonify({"status": False, "error": "Отсутствуют обязательные поля: student_id, year_month"}), 400
        
        result = get_student_attendance(student_id, year_month)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500


# ==================== EXAMS ROUTES ====================

@app.route("/get-all-exams")
def get_all_exams_route():
    """Получает все экзамены"""
    result = get_all_exams()
    return jsonify(result)

@app.route("/get-exam-session", methods=["POST"])
@require_self_or_role('student_id', 'admin')
def get_exam_session_route(current_user=None):
    """Получает сессию экзамена для студента"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        exam_id = data.get('exam_id')
        
        if not student_id or not exam_id:
            return jsonify({
                "status": False,
                "error": "Отсутствуют обязательные поля: student_id, exam_id"
            }), 400
        
        result = get_exam_session(student_id, exam_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

@app.route("/get-student-exam-sessions/<student_id>")
@require_self_or_role('student_id', 'admin')
def get_student_exam_sessions_route(student_id, current_user=None):
    """Получает все сессии экзаменов для студента"""
    result = get_exam_sessions_by_student(student_id)
    return jsonify(result)

@app.route("/get-all-exam-sessions")
@require_role('admin')
def get_all_exam_sessions_route(current_user=None):
    """Получает все сессии экзаменов (для администраторов)"""
    result = get_all_exam_sessions()
    return jsonify(result)

@app.route("/get-exam-sessions/<exam_id>")
@require_role('admin')
def get_exam_sessions_by_exam_route(exam_id, current_user=None):
    """Получает все сессии для конкретного экзамена"""
    result = get_exam_sessions_by_exam(exam_id)
    return jsonify(result)


# ==================== EXTERNAL TESTS ROUTES ====================

@app.route("/external-tests/direction/<direction_id>")
@require_auth
def get_external_tests_by_direction_route(direction_id, current_user=None):
    """
    Получает внешние тесты по ID направления
    Для студентов возвращает тесты с их результатами
    Для админов возвращает все тесты
    """
    student_id = current_user.get('id') if current_user else None
    
    if student_id and current_user.get('role') == 'student':
        # Для студентов получаем тесты с результатами
        external_tests = get_external_tests_with_results_by_student(direction_id, student_id)
    else:
        # Для админов и других ролей получаем все внешние тесты
        external_tests = get_all_external_tests_by_direction_for_admin(direction_id)
    
    return jsonify(external_tests)

@app.route("/external-tests/student/<student_id>/direction/<direction_id>")
@require_self_or_role('student_id', 'admin')
def get_external_tests_for_student_route(student_id, direction_id, current_user=None):
    """
    Получает внешние тесты направления с результатами конкретного студента
    """
    external_tests = get_external_tests_with_results_by_student(direction_id, student_id)
    return jsonify(external_tests)


# ==================== RATINGS ROUTES ====================

@app.route("/get-all-ratings", methods=['GET'])
@require_role('admin', 'supervisor')
def get_all_ratings_route(current_user=None):
    """
    Получает все рейтинги из таблицы Allratings
    Для администраторов и супервайзеров
    
    Возвращает:
    {
        "status": true/false,
        "ratings": [
            {
                "id": 1,
                "student_id": 123,
                "exams": 4.5,
                "homework": 85.2,
                "tests": 78.3,
                "final": 92.5
            },
            ...
        ]
    }
    """
    mysql_conn = None
    try:
        mysql_conn = get_db_connection()
        cursor = mysql_conn.cursor(dictionary=True)
        
        # Получаем все рейтинги с информацией о студентах
        query = """
            SELECT 
                ar.id,
                ar.student_id,
                ar.exams,
                ar.homework,
                ar.tests,
                ar.final,
                s.full_name as student_name,
                s.class as student_class,
                g.name as group_name
            FROM Allratings ar
            LEFT JOIN students s ON ar.student_id = s.id
            LEFT JOIN `groups` g ON s.group_id = g.id
            ORDER BY ar.final DESC, s.full_name ASC
        """
        
        cursor.execute(query)
        ratings = cursor.fetchall()
        
        # Форматируем результаты
        formatted_ratings = []
        for rating in ratings:
            formatted_ratings.append({
                'id': rating['id'],
                'student_id': rating['student_id'],
                'student_name': rating.get('student_name', 'Неизвестно'),
                'student_class': rating.get('student_class'),
                'group_name': rating.get('group_name'),
                'exams': float(rating['exams']) if rating['exams'] is not None else 0,
                'homework': float(rating['homework']) if rating['homework'] is not None else 0,
                'tests': float(rating['tests']) if rating['tests'] is not None else 0,
                'final': float(rating['final']) if rating['final'] is not None else 0
            })
        
        return jsonify({
            "status": True,
            "ratings": formatted_ratings,
            "total": len(formatted_ratings)
        })
        
    except Exception as e:
        return jsonify({
            "status": False,
            "error": f"Внутренняя ошибка сервера: {str(e)}"
        }), 500
    finally:
        if mysql_conn:
            close_db_connection(mysql_conn)


@app.route("/get-rating-details", methods=['POST'])
@require_role('admin', 'supervisor')
def get_rating_details_route(current_user=None):
    """
    Получает детализацию рейтинга по ID записи из MongoDB
    Для администраторов и супервайзеров
    
    Ожидаемые данные в JSON:
    {
        "rating_id": 123  // ID записи из таблицы Allratings
    }
    
    Возвращает:
    {
        "status": true/false,
        "details": {
            "rating_id": 123,
            "student_id": 456,
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "calculated_at": "...",
            "homework": {...},
            "exams": {...},
            "tests": {...},
            "final_rating": 92.5
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": False,
                "error": "Данные не предоставлены"
            }), 400
        
        rating_id = data.get('rating_id')
        
        if not rating_id:
            return jsonify({
                "status": False,
                "error": "rating_id обязателен"
            }), 400
        
        # Приводим к int
        try:
            rating_id = int(rating_id)
        except (ValueError, TypeError):
            return jsonify({
                "status": False,
                "error": "rating_id должен быть числом"
            }), 400
        
        # Подключаемся к MongoDB
        mongo_client = MongoClient('mongodb://gen_user:I_OBNu~9oHF0(m@81.200.148.71:27017/default_db?authSource=admin&directConnection=true')
        db_mongo = mongo_client.default_db
        rate_rec_collection = db_mongo.rate_rec
        
        # Ищем детализацию по rating_id
        details = rate_rec_collection.find_one({'rating_id': rating_id})
        mongo_client.close()
        
        if not details:
            return jsonify({
                "status": False,
                "error": f"Детализация для rating_id {rating_id} не найдена"
            }), 404
        
        # Преобразуем ObjectId в строку
        if '_id' in details:
            details['_id'] = str(details['_id'])
        
        return jsonify({
            "status": True,
            "details": details
        })
        
    except Exception as e:
        return jsonify({
            "status": False,
            "error": f"Внутренняя ошибка сервера: {str(e)}"
        }), 500


@app.route("/calculate-all-ratings", methods=['POST'])
@require_role('admin')
def calculate_all_ratings_route(current_user=None):
    """
    Рассчитывает и сохраняет рейтинги для всех студентов
    Только для администраторов
    
    Ожидаемые данные в JSON:
    {
        "date_from": "2024-01-01",
        "date_to": "2024-12-31"
    }
    
    Возвращает:
    {
        "status": true/false,
        "message": "...",
        "results": {
            "total_students": 100,
            "successful": 95,
            "failed": 5,
            "errors": [...]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": False,
                "error": "Данные не предоставлены"
            }), 400
        
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if not date_from or not date_to:
            return jsonify({
                "status": False,
                "error": "date_from и date_to обязательны"
            }), 400
        
        # Валидация формата дат
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "status": False,
                "error": "Неверный формат даты. Ожидается YYYY-MM-DD"
            }), 400
        
        # Получаем подключение из пула
        mysql_conn = get_db_connection()
        mongo_client = MongoClient('mongodb://gen_user:I_OBNu~9oHF0(m@81.200.148.71:27017/default_db?authSource=admin&directConnection=true')
        
        try:
            # Рассчитываем и сохраняем рейтинги
            # (внутри функции уже происходит очистка таблиц)
            results = save_all_ratings(mysql_conn, mongo_client, date_from, date_to)
            
            # Формируем сообщение
            message_parts = [f"Обработано студентов: {results['successful']}/{results['total_students']}"]
            if results.get('skipped', 0) > 0:
                message_parts.append(f"Пропущено: {results['skipped']}")
            if results.get('failed', 0) > 0:
                message_parts.append(f"Ошибок: {results['failed']}")
            
            return jsonify({
                "status": True,
                "message": " | ".join(message_parts),
                "results": results
            })
            
        finally:
            if mysql_conn:
                close_db_connection(mysql_conn)
            if mongo_client:
                mongo_client.close()
            
    except Exception as e:
        return jsonify({
            "status": False,
            "error": f"Внутренняя ошибка сервера: {str(e)}"
        }), 500


if __name__ =="__main__":
    app.run(host='0.0.0.0', port=81,debug=False,threaded=True)
 
