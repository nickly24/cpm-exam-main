from create_test import create_test
from datetime import datetime

# Данные теста на 22 сентября 2025 года
test_data = {
    "title": "Экзамен по программированию - 22 сентября 2025",
    "direction": "Программирование",
    "startDate": "2025-09-22T00:00:00Z",
    "endDate": "2026-09-22T23:59:59Z",  # Доступен 1 год
    "timeLimitMinutes": 60,  # 1 час
    "questions": [
        {
            "questionId": 1,
            "type": "single",
            "text": "Какой язык программирования является интерпретируемым?",
            "points": 10,
            "answers": [
                {"id": "a", "text": "C++", "isCorrect": False},
                {"id": "b", "text": "Python", "isCorrect": True},
                {"id": "c", "text": "Java", "isCorrect": False},
                {"id": "d", "text": "C#", "isCorrect": False}
            ]
        },
        {
            "questionId": 2,
            "type": "multiple",
            "text": "Какие из перечисленных являются типами данных в Python?",
            "points": 15,
            "answers": [
                {"id": "a", "text": "int", "isCorrect": True, "pointValue": 5},
                {"id": "b", "text": "string", "isCorrect": False, "pointValue": 0},
                {"id": "c", "text": "list", "isCorrect": True, "pointValue": 5},
                {"id": "d", "text": "array", "isCorrect": False, "pointValue": 0}
            ]
        },
        {
            "questionId": 3,
            "type": "text",
            "text": "Как называется функция для вывода текста в консоль в Python?",
            "points": 10,
            "correctAnswers": ["print", "print()"]
        },
        {
            "questionId": 4,
            "type": "single",
            "text": "Что выведет код: print(2 ** 3)?",
            "points": 10,
            "answers": [
                {"id": "a", "text": "6", "isCorrect": False},
                {"id": "b", "text": "8", "isCorrect": True},
                {"id": "c", "text": "9", "isCorrect": False},
                {"id": "d", "text": "Ошибку", "isCorrect": False}
            ]
        },
        {
            "questionId": 5,
            "type": "single",
            "text": "Какой символ используется для комментариев в Python?",
            "points": 5,
            "answers": [
                {"id": "a", "text": "//", "isCorrect": False},
                {"id": "b", "text": "#", "isCorrect": True},
                {"id": "c", "text": "/*", "isCorrect": False},
                {"id": "d", "text": "--", "isCorrect": False}
            ]
        }
    ],
    "isActive": True
}

# Создаем тест
test_id = create_test(test_data)
print(f"Тест успешно создан с ID: {test_id}")
print(f"Название: {test_data['title']}")
print(f"Направление: {test_data['direction']}")
print(f"Дата начала: {test_data['startDate']}")
print(f"Дата окончания: {test_data['endDate']}")
print(f"Время на прохождение: {test_data['timeLimitMinutes']} минут")
print(f"Количество вопросов: {len(test_data['questions'])}")

