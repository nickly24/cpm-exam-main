from db import db
from flask import Flask, jsonify, request
from flask_cors import CORS 
from get_question_byiD import get_question_by_id
from get_random_question_by_themeID import get_random_question_by_theme
from get_all_themes import get_all_themes
from getl_all_exams import get_all_exams
from exam_report import get_all_exam_sessions
from add_exam_session import create_exam_session
from add_exam_answer import add_exam_answer
from update_exam_result import update_exam_result
from get_random_qusetion_by_examid import get_random_question_by_exam
from get_exam_session import get_exam_session_by_student_and_exam
from attendance_by_date import get_attendance_by_student
from get_bracnhes_by_students import get_student_tests_grouped_by_branch
from get_ques_with_answers import get_test_with_questions_and_answers
from create_test_session import create_test_session
from student_perfomance import calculate_students_performance
from perfomance_by_studentid import get_student_study_summary
from create_test import create_test_with_questions_and_answers
from create_exam import create_exam_with_questions
from get_all_branchnes import get_all_test_branches
from calculate_rating import fill_rating_table_by_period
from get_all_rating import get_all_students_with_rating
from get_class_name_by_studID import get_student_name_and_class
from get_rating_by_student_id import get_rating_by_student_id
from get_exams_w_results import get_exams_w_results
from get_tests_w_results import get_tests_w_results
from delete_exam import delete_exam



app = Flask(__name__)
CORS(app)
@app.route("/")
def hello_world():
    return jsonify({"answer": "poshel nahooy"})

@app.route("/get-questions-byid", methods = ["POST"]) 
def getQues():
    req=request.get_json()
    id=req.get("id")
    answer=get_question_by_id(id)
    return jsonify(answer)


@app.route("/get-random-question-by-themeid", methods=["POST"])
def get_random_question():
    req = request.get_json()
    theme_id = req.get("theme_id")  # <-- это ключ, который ожидаем из JSON
    result = get_random_question_by_theme(theme_id)
    return jsonify(result)


@app.route("/get-all-themes") 
def getALLthemes():
    answer=get_all_themes()
    return jsonify(answer)


@app.route("/get-all-exams") 
def getALLexams():
    answer=get_all_exams()
    return jsonify(answer)
 
@app.route("/exam-report") 
def getallexamsessions():
    answer=get_all_exam_sessions()
    return jsonify(answer)


@app.route("/add-exam-session", methods=["POST"])
def add_exam_session_route():
    req = request.get_json()
    student_id = req.get("student_id")
    exam_id = req.get("exam_id")
    result = create_exam_session(student_id, exam_id)
    return jsonify(result)

@app.route("/add-exam-answer", methods=["POST"])
def add_answer_route():
    req = request.get_json()
    exam_session_id = req.get("exam_session_id")
    question_id = req.get("question_id")
    result = req.get("result")
    return jsonify(add_exam_answer(exam_session_id, question_id, result))


@app.route("/update-exam-result", methods=["POST"])
def update_exam_result_route():
    req = request.get_json()
    exam_session_id = req.get("exam_session_id")
    result = req.get("result")
    return jsonify(update_exam_result(exam_session_id, result))


@app.route("/get-random-question-by-examid", methods=["POST"])
def get_random_question_by_exam_route():
    req = request.get_json()
    exam_id = req.get("exam_id")
    result = get_random_question_by_exam(exam_id)
    return jsonify(result)


@app.route("/get-exam-session", methods=["POST"])
def get_exam_session_route():
    # Получает экзаменационную сессию по ID ученика и ID экзамена
    # Вход: { "student_id": <id>, "exam_id": <id> }
    req = request.get_json()
    student_id = req.get("student_id")
    exam_id = req.get("exam_id")
    return jsonify(get_exam_session_by_student_and_exam(student_id, exam_id))


@app.route("/get-attendance", methods=["POST"])
def get_attendance_route():
    """
    Получает посещаемость по ID студента и дате (год-месяц)
    Вход: { "student_id": <id>, "year_month": "2025-06" }
    """
    req = request.get_json()
    student_id = req.get("student_id")
    year_month = req.get("year_month")  # строка формата "2025-06"
    result = get_attendance_by_student (student_id, year_month)
    return jsonify(result)


@app.route("/get-student-tests", methods=["POST"])
def get_student_tests_route():
    data = request.get_json()
    student_id = data.get("student_id")
    result = get_student_tests_grouped_by_branch(student_id)
    return jsonify(result)


@app.route("/get-ques-with-answers", methods=["POST"])
def get_test_questions_route():
    data = request.get_json()
    test_id = data.get("test_id")
    result = get_test_with_questions_and_answers(test_id)
    return jsonify(result)


@app.route("/create-test-session", methods=["POST"])
def create_test_session_route():
    data = request.get_json()
    test_id = data.get("test_id")
    student_id = data.get("student_id")
    result = data.get("result")
    return jsonify(create_test_session(test_id, student_id, result))

@app.route("/get-performance", methods=["POST"])
def get_students_performance_route():
    data = request.get_json()
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    result = calculate_students_performance(start_date, end_date)
    return jsonify(result)


@app.route("/perfomance-by-student", methods=["POST"])
def get_student_summary_route():
    data = request.get_json()
    student_id = data.get("student_id")
    summary = get_student_study_summary(student_id)
    return jsonify({"status": True, "data": summary})

@app.route("/create-test", methods=["POST"])
def create_test_route():
    data = request.get_json()
    result = create_test_with_questions_and_answers(data)
    return jsonify({"status": True, "data": result})


@app.route("/create-exam", methods=["POST"])
def create_exam_route():
    data = request.get_json()
    result = create_exam_with_questions(data)
    return jsonify({"status": True, "data": result})


@app.route("/get-all-branchnes", methods=["GET"])
def get_branches_route():
    result = get_all_test_branches()
    return jsonify({"status": True, "data": result})


@app.route("/calculate-rating", methods=["GET"])
def update_rating():
    result = fill_rating_table_by_period()
    return jsonify({"status": True, "data": result})


@app.route("/get-all-rating", methods=["GET"])
def get_students_with_rating_route():
    result = get_all_students_with_rating()
    return jsonify({"status ": True, "data": result})


@app.route("/get-class-name-by-studID", methods=["POST"])
def student_info():
    data = request.get_json()
    student_id = data.get("student_id")
    result = get_student_name_and_class(student_id)
    return jsonify({"status": True, "data": result})


@app.route("/student-rating", methods=["POST"])
def student_rating():
    data = request.get_json()
    student_id = data.get("student_id")
    result = get_rating_by_student_id(student_id)
    return jsonify({"status": True, "data": result})


@app.route("/get-exams-w-results-student", methods=["POST"])
def route1():
    data = request.get_json()
    student_id = data.get("student_id")
    result = get_exams_w_results(student_id)
    return jsonify(result)


@app.route("/delete-exam", methods=["POST"])
def route2():
    data = request.get_json()
    exam_id = data.get("exam_id")
    result = delete_exam(exam_id)
    return jsonify(result)


@app.route("/get-tests-w-results-student", methods=["POST"])
def route3():
    data = request.get_json()
    student_id = data.get("student_id")
    result = get_tests_w_results(student_id)
    return jsonify(result)


if __name__ =="__main__":
    app.run(host='0.0.0.0', port=80,debug=True)
 
