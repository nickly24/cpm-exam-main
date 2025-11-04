from db import db
from flask import Flask, jsonify, request
from flask_cors import CORS
from jwt_auth import require_auth, require_role, require_self_or_role
from get_directions import get_directions
from get_tests_by_direction import get_tests_by_direction
from create_test import create_test, update_test, delete_test, get_test_by_id
from create_test_session import create_test_session, get_test_session_by_id, get_test_sessions_by_student, get_test_sessions_by_test, get_test_session_stats, get_test_session_by_student_and_test, recalc_test_sessions
from get_student_attendance import get_student_attendance
from get_exams import get_all_exams, get_exam_session, get_exam_sessions_by_student, get_all_exam_sessions, get_exam_sessions_by_exam
from get_external_tests import get_external_tests_with_results_by_student, get_all_external_tests_by_direction_for_admin 




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


if __name__ =="__main__":
    app.run(host='0.0.0.0', port=81,debug=True)
 
