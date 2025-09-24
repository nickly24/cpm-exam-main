from db import db
from flask import Flask, jsonify, request
from flask_cors import CORS
from get_directions import get_directions
from get_tests_by_direction import get_tests_by_direction
from create_test import create_test, update_test, delete_test, get_test_by_id
from create_test_session import create_test_session, get_test_session_by_id, get_test_sessions_by_student, get_test_sessions_by_test, get_test_session_stats, get_test_session_by_student_and_test, recalc_test_sessions 




app = Flask(__name__)
CORS(app, resources={
    r"/*": {  # Обратите внимание на "/*" вместо "/api/*"
        "origins": "*",  # Только ваш фронтенд
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
@app.route("/")
def hello_world():
    return jsonify({"answer": "poshel nahooy"})

@app.route("/directions")
def get_directions_route():
    directions = get_directions()
    return jsonify(directions)

@app.route("/tests/<direction>")
def get_tests_by_direction_route(direction):
    tests = get_tests_by_direction(direction)
    return jsonify(tests)

@app.route("/test/<test_id>")
def get_test_by_id_route(test_id):
    test = get_test_by_id(test_id)
    if test:
        return jsonify(test)
    return jsonify({"error": "Test not found"}), 404

@app.route("/create-test", methods=["POST"])
def create_test_route():
    test_data = request.get_json()
    test_id = create_test(test_data)
    return jsonify({"id": test_id})

@app.route("/test/<test_id>", methods=["PUT"])
def update_test_route(test_id):
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
def delete_test_route(test_id):
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
def create_test_session_route():
    session_data = request.get_json()
    
    # Проверяем обязательные поля
    required_fields = ["studentId", "testId", "testTitle", "answers"]
    for field in required_fields:
        if field not in session_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    session_id = create_test_session(
        student_id=session_data["studentId"],
        test_id=session_data["testId"],
        test_title=session_data["testTitle"],
        answers=session_data["answers"],
        score=session_data.get("score"),
        time_spent_minutes=session_data.get("timeSpentMinutes")
    )
    
    return jsonify({"id": session_id})

@app.route("/test-session/<session_id>")
def get_test_session_route(session_id):
    session = get_test_session_by_id(session_id)
    if session:
        return jsonify(session)
    return jsonify({"error": "Test session not found"}), 404

@app.route("/test-sessions/student/<student_id>")
def get_test_sessions_by_student_route(student_id):
    sessions = get_test_sessions_by_student(student_id)
    return jsonify(sessions)

@app.route("/test-sessions/test/<test_id>")
def get_test_sessions_by_test_route(test_id):
    sessions = get_test_sessions_by_test(test_id)
    return jsonify(sessions)

@app.route("/test-session/<session_id>/stats")
def get_test_session_stats_route(session_id):
    stats = get_test_session_stats(session_id)
    if stats:
        return jsonify(stats)
    return jsonify({"error": "Test session not found"}), 404

@app.route("/test-session/student/<student_id>/test/<test_id>")
def get_test_session_by_student_and_test_route(student_id, test_id):
    session = get_test_session_by_student_and_test(student_id, test_id)
    if session:
        return jsonify(session)
    return jsonify({"error": "Test session not found"}), 404



if __name__ =="__main__":
    app.run(host='0.0.0.0', port=81,debug=True)
 
