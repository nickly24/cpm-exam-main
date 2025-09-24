from create_test_session import create_test_session, get_test_session_by_id, get_test_sessions_by_student, get_test_session_stats

# Пример данных тест-сессии
student_id = "student_12345"
test_id = "68b8506b0bb37f22653b3550"  # ID теста из существующего теста
test_title = "Экзамен по программированию - 22 сентября 2025"

# Ответы студента на вопросы
answers = [
    {
        "questionId": 1,
        "type": "single",
        "selectedAnswer": "b",  # Выбрал Python
        "isCorrect": True,
        "points": 10  # Набрал 10 баллов за правильный ответ
    },
    {
        "questionId": 2,
        "type": "multiple",
        "selectedAnswers": ["a", "c"],  # Выбрал int и list
        "isCorrect": True,
        "points": 10  # Набрал 10 баллов (5+5) за правильные ответы
    },
    {
        "questionId": 3,
        "type": "text",
        "textAnswer": "print",  # Написал print
        "isCorrect": True,
        "points": 10  # Набрал 10 баллов за правильный ответ
    },
    {
        "questionId": 4,
        "type": "single",
        "selectedAnswer": "b",  # Выбрал 8
        "isCorrect": True,
        "points": 10  # Набрал 10 баллов за правильный ответ
    },
    {
        "questionId": 5,
        "type": "single",
        "selectedAnswer": "b",  # Выбрал #
        "isCorrect": True,
        "points": 5  # Набрал 5 баллов за правильный ответ
    }
]

# Создаем тест-сессию
session_id = create_test_session(
    student_id=student_id,
    test_id=test_id,
    test_title=test_title,
    answers=answers,
    # score не указываем - будет автоматически вычислен из points в answers (45 баллов)
    time_spent_minutes=45  # Потратил 45 минут
)

print(f"Тест-сессия успешно создана с ID: {session_id}")
print(f"Студент: {student_id}")
print(f"Тест: {test_title}")
print(f"Набранные баллы: 45/50")  # 10+10+10+10+5 = 45 баллов
print(f"Время прохождения: 45 минут")

# Получаем созданную сессию
session = get_test_session_by_id(session_id)
if session:
    print(f"\nДетали сессии:")
    print(f"ID сессии: {session['_id']}")
    print(f"Дата завершения: {session['completedAt']}")
    print(f"Количество ответов: {len(session['answers'])}")

# Получаем детальную статистику по сессии
stats = get_test_session_stats(session_id)
if stats:
    print(f"\n📊 Детальная статистика сессии:")
    print(f"Общее количество вопросов: {stats['totalQuestions']}")
    print(f"Правильных ответов: {stats['correctAnswers']}")
    print(f"Точность: {stats['accuracy']}%")
    print(f"Общий балл: {stats['totalPoints']}")
    print(f"Время прохождения: {stats['timeSpentMinutes']} минут")
    
    print(f"\n📈 Статистика по типам вопросов:")
    for q_type, data in stats['questionTypes'].items():
        accuracy = (data['correct'] / data['count']) * 100 if data['count'] > 0 else 0
        print(f"- {q_type}: {data['correct']}/{data['count']} ({accuracy:.1f}%) - {data['points']} баллов")

# Получаем все сессии студента
student_sessions = get_test_sessions_by_student(student_id)
print(f"\n📚 Всего сессий у студента {student_id}: {len(student_sessions)}")
for session in student_sessions:
    print(f"- {session['testTitle']} (баллы: {session['score']}, дата: {session['completedAt']})")
