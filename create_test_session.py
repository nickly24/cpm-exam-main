from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError

client = MongoClient('mongodb://gen_user:77tanufe@109.73.202.73:27017/default_db?authSource=admin&directConnection=true')

# Создаем уникальный индекс для предотвращения дублирования тест-сессий
def ensure_unique_index():
    """Создает уникальный индекс для предотвращения дублирования тест-сессий"""
    db = client.default_db
    test_sessions_collection = db.test_sessions
    
    try:
        # Создаем уникальный составной индекс по studentId и testId
        test_sessions_collection.create_index(
            [("studentId", 1), ("testId", 1)],
            unique=True,
            name="unique_student_test"
        )
        print("Уникальный индекс создан успешно")
    except Exception as e:
        print(f"Ошибка при создании индекса: {e}")

# Вызываем создание индекса при импорте модуля
ensure_unique_index()

def create_test_session(student_id, test_id, test_title, answers, score=None, time_spent_minutes=None):
    """
    Создает тест-сессию с ответами студента
    
    Args:
        student_id (str): ID студента
        test_id (str): ID теста
        test_title (str): Название теста
        answers (list): Список ответов студента (каждый ответ должен содержать points)
        score (int, optional): Набранные баллы (автоматически вычисляется из answers если не указан)
        time_spent_minutes (int, optional): Время прохождения в минутах
    
    Returns:
        dict: Результат создания сессии с информацией о дублировании
    """
    db = client.default_db
    test_sessions_collection = db.test_sessions
    
    # Проверяем, не существует ли уже тест-сессия для этого студента и теста
    existing_session = test_sessions_collection.find_one({
        "studentId": student_id,
        "testId": test_id
    })
    
    if existing_session:
        return {
            "success": False,
            "error": "Тест уже сдан",
            "message": "Для данного студента и теста уже существует завершенная сессия",
            "existingSessionId": str(existing_session["_id"]),
            "existingScore": existing_session.get("score"),
            "completedAt": existing_session.get("completedAt")
        }
    
    # Автоматически вычисляем общий балл, если не указан
    if score is None:
        score = sum(int(answer.get("points", 0)) for answer in answers)
    
    # Создаем объект тест-сессии
    test_session = {
        "studentId": student_id,
        "testId": test_id,
        "testTitle": test_title,
        "answers": answers,
        "score": score,
        "timeSpentMinutes": time_spent_minutes,
        "completedAt": datetime.utcnow().isoformat() + "Z",
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }
    
    # Вставляем в базу данных с дополнительной защитой от дублирования
    try:
        result = test_sessions_collection.insert_one(test_session)
        
        return {
            "success": True,
            "sessionId": str(result.inserted_id),
            "message": "Тест-сессия успешно создана"
        }
    except DuplicateKeyError:
        # Если все же произошло дублирование на уровне БД (редкий случай)
        # Ищем существующую сессию и возвращаем информацию о ней
        existing_session = test_sessions_collection.find_one({
            "studentId": student_id,
            "testId": test_id
        })
        
        return {
            "success": False,
            "error": "Тест уже сдан",
            "message": "Обнаружено дублирование на уровне базы данных",
            "existingSessionId": str(existing_session["_id"]) if existing_session else None,
            "existingScore": existing_session.get("score") if existing_session else None,
            "completedAt": existing_session.get("completedAt") if existing_session else None
        }

def get_test_session_by_id(session_id):
    """
    Получает тест-сессию по ID
    
    Args:
        session_id (str): ID тест-сессии
    
    Returns:
        dict: Данные тест-сессии или None
    """
    from bson import ObjectId
    
    db = client.default_db
    test_sessions_collection = db.test_sessions
    
    session = test_sessions_collection.find_one({"_id": ObjectId(session_id)})
    
    if session:
        session["_id"] = str(session["_id"])
        return session
    
    return None

def get_test_sessions_by_student(student_id):
    """
    Получает все тест-сессии студента
    
    Args:
        student_id (str): ID студента
    
    Returns:
        list: Список тест-сессий студента
    """
    db = client.default_db
    test_sessions_collection = db.test_sessions
    
    sessions = test_sessions_collection.find(
        {"studentId": student_id},
        {"_id": 1, "testId": 1, "testTitle": 1, "score": 1, "completedAt": 1, "timeSpentMinutes": 1}
    ).sort("completedAt", -1)  # Сортируем по дате завершения (новые сверху)
    
    result = []
    for session in sessions:
        result.append({
            "id": str(session["_id"]),
            "testId": session["testId"],
            "testTitle": session["testTitle"],
            "score": session.get("score"),
            "completedAt": session["completedAt"],
            "timeSpentMinutes": session.get("timeSpentMinutes")
        })
    
    return result

def get_test_sessions_by_test(test_id):
    """
    Получает все тест-сессии по конкретному тесту
    
    Args:
        test_id (str): ID теста
    
    Returns:
        list: Список тест-сессий по тесту
    """
    db = client.default_db
    test_sessions_collection = db.test_sessions
    
    sessions = test_sessions_collection.find(
        {"testId": test_id},
        {"_id": 1, "studentId": 1, "testTitle": 1, "score": 1, "completedAt": 1, "timeSpentMinutes": 1}
    ).sort("completedAt", -1)
    
    result = []
    for session in sessions:
        result.append({
            "id": str(session["_id"]),
            "studentId": session["studentId"],
            "testTitle": session["testTitle"],
            "score": session.get("score"),
            "completedAt": session["completedAt"],
            "timeSpentMinutes": session.get("timeSpentMinutes")
        })
    
    return result

def get_test_session_stats(session_id):
    """
    Получает детальную статистику по тест-сессии
    
    Args:
        session_id (str): ID тест-сессии
    
    Returns:
        dict: Статистика по сессии
    """
    from bson import ObjectId
    
    db = client.default_db
    test_sessions_collection = db.test_sessions
    
    session = test_sessions_collection.find_one({"_id": ObjectId(session_id)})
    
    if not session:
        return None
    
    # Подсчитываем статистику по ответам
    total_questions = len(session["answers"])
    correct_answers = sum(1 for answer in session["answers"] if answer.get("isCorrect", False))
    total_points = sum(int(answer.get("points", 0)) for answer in session["answers"])
    
    # Группируем по типам вопросов
    question_types = {}
    for answer in session["answers"]:
        q_type = answer.get("type", "unknown")
        if q_type not in question_types:
            question_types[q_type] = {"count": 0, "correct": 0, "points": 0}
        
        question_types[q_type]["count"] += 1
        if answer.get("isCorrect", False):
            question_types[q_type]["correct"] += 1
        question_types[q_type]["points"] += int(answer.get("points", 0))
    
    stats = {
        "sessionId": str(session["_id"]),
        "studentId": session["studentId"],
        "testTitle": session["testTitle"],
        "totalQuestions": total_questions,
        "correctAnswers": correct_answers,
        "accuracy": round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0,
        "totalPoints": total_points,
        "timeSpentMinutes": session.get("timeSpentMinutes"),
        "completedAt": session["completedAt"],
        "questionTypes": question_types,
        "answers": session["answers"]
    }
    
    return stats

def get_test_session_by_student_and_test(student_id, test_id):
    """
    Получает тест-сессию по ID студента и ID теста
    
    Args:
        student_id (str): ID студента
        test_id (str): ID теста
    
    Returns:
        dict: Данные тест-сессии или None
    """
    db = client.default_db
    test_sessions_collection = db.test_sessions
    
    session = test_sessions_collection.find_one({
        "studentId": student_id,
        "testId": test_id
    })
    
    if session:
        session["_id"] = str(session["_id"])
        return session
    
    return None

# ===================== ПЕРЕСЧЕТ РЕЗУЛЬТАТОВ СЕССИЙ ПОСЛЕ ОБНОВЛЕНИЯ ТЕСТА =====================
def _normalize_text(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()

def _score_single(selected_answer_id: str, question: dict) -> tuple[int, bool]:
    correct_ids = {a.get("id") for a in question.get("answers", []) if a.get("isCorrect")}
    is_correct = selected_answer_id in correct_ids
    points = int(question.get("points", 0)) if is_correct else 0
    return points, is_correct

def _score_multiple(selected_answer_ids: list, question: dict) -> tuple[int, bool]:
    """
    Правильная логика для множественного выбора:
    - Должны быть выбраны ВСЕ правильные ответы
    - Не должно быть выбрано НИ ОДНОГО неправильного ответа
    - Иначе - 0 баллов
    """
    total_available = int(question.get("points", 0))
    answers_index = {a.get("id"): a for a in question.get("answers", [])}
    selected_set = set(selected_answer_ids or [])
    
    # Получаем все правильные ответы (только те, где isCorrect = true)
    all_correct_ids = {a.get("id") for a in question.get("answers", []) if a.get("isCorrect")}
    
    # Получаем все неправильные ответы
    all_incorrect_ids = {a.get("id") for a in question.get("answers", []) if not a.get("isCorrect")}
    
    # Проверка 1: Выбраны ВСЕ правильные ответы
    all_correct_selected = selected_set.issuperset(all_correct_ids)
    
    # Проверка 2: НЕ выбрано НИ ОДНОГО неправильного ответа
    no_incorrect_selected = selected_set.isdisjoint(all_incorrect_ids)
    
    # Если обе проверки пройдены - даем полные баллы
    if all_correct_selected and no_incorrect_selected:
        return total_available, True
    else:
        # Иначе - 0 баллов
        return 0, False

def _score_text(text_answer: str, question: dict) -> tuple[int, bool]:
    """
    Правильная логика для текстового ответа:
    - Буква в букву (с учетом нормализации)
    - Совпадение с одним из правильных ответов
    """
    normalized = _normalize_text(text_answer)
    correct_list = [
        _normalize_text(val) for val in (question.get("correctAnswers") or [])
    ]
    is_correct = normalized in correct_list if correct_list else False
    points = int(question.get("points", 0)) if is_correct else 0
    return points, is_correct

def _recompute_answer(existing_answer: dict, question: dict) -> dict:
    a_type = existing_answer.get("type") or question.get("type")
    updated = dict(existing_answer)
    if a_type == "single":
        pts, ok = _score_single(existing_answer.get("selectedAnswer"), question)
    elif a_type == "multiple":
        pts, ok = _score_multiple(existing_answer.get("selectedAnswers", []), question)
    elif a_type == "text":
        pts, ok = _score_text(existing_answer.get("textAnswer"), question)
    else:
        pts, ok = 0, False
    updated["type"] = a_type
    updated["points"] = int(pts)
    updated["isCorrect"] = bool(ok)
    return updated

def _placeholder_answer_for_new_question(question: dict) -> dict:
    a_type = question.get("type")
    base = {
        "questionId": question.get("questionId"),
        "type": a_type,
        "points": 0,
        "isCorrect": False,
    }
    if a_type == "single":
        base["selectedAnswer"] = None
    elif a_type == "multiple":
        base["selectedAnswers"] = []
    elif a_type == "text":
        base["textAnswer"] = ""
    return base

def recalc_test_sessions(test_id: str) -> dict:
    """
    Пересчитывает все тест-сессии для указанного теста по текущей версии теста.

    Логика:
    - Для вопросов, которые были УДАЛЕНЫ из теста: существующие ответы помечаются 0 баллов и isCorrect=False.
    - Для вопросов, которые были ДОБАВЛЕНЫ в тест: в сессии добавляется ответ-заглушка с 0 баллов и isCorrect=False.
    - Для измененных вопросов: ответы пересчитываются по актуальной специфике вопросов/ответов.

    Returns:
        dict: статистика пересчета.
    """
    db = client.default_db
    tests_collection = db.tests
    sessions_collection = db.test_sessions

    from bson import ObjectId
    test = tests_collection.find_one({"_id": ObjectId(test_id)})
    if not test:
        return {"updated": 0, "sessions": 0, "error": "Test not found"}

    # Индексы вопросов по questionId
    questions = test.get("questions", [])
    question_by_id = {q.get("questionId"): q for q in questions}
    current_title = test.get("title")

    sessions_cursor = sessions_collection.find({"testId": test_id})
    updated_count = 0
    total_sessions = 0

    for session in sessions_cursor:
        total_sessions += 1
        answers = session.get("answers", [])
        answer_by_qid = {a.get("questionId"): a for a in answers if "questionId" in a}

        new_answers: list[dict] = []

        # 1) Пройтись по ответам: если вопрос удален — убираем из сессии; если есть в тесте — пересчитываем
        for a in answers:
            qid = a.get("questionId")
            q_spec = question_by_id.get(qid)
            if not q_spec:
                # Вопрос удален — полностью убираем из сессии
                continue
            else:
                # Пересчитываем по новой спецификации
                new_answers.append(_recompute_answer(a, q_spec))

        # 2) Добавить ответы-заглушки для новых вопросов, на которые не отвечали
        for q in questions:
            qid = q.get("questionId")
            if qid not in answer_by_qid:
                new_answers.append(_placeholder_answer_for_new_question(q))

        # 3) Пересчитать рейтинговый балл
        earned_points = sum(int(a.get("points", 0)) for a in new_answers)
        max_points = sum(int(q.get("points", 0)) for q in questions)
        
        # Рейтинговый балл = (набранные баллы / максимальные баллы) × 100
        if max_points > 0:
            new_score = round((earned_points / max_points) * 100, 2)
        else:
            new_score = 0

        update_doc = {
            "answers": new_answers,
            "score": int(new_score),
            # Обновим заголовок теста в сессии, если он изменился
            "testTitle": current_title if current_title else session.get("testTitle"),
        }

        result = sessions_collection.update_one({"_id": session["_id"]}, {"$set": update_doc})
        if result.modified_count:
            updated_count += 1

    return {"updated": int(updated_count), "sessions": int(total_sessions)}
