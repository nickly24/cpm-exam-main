ДОКУМЕНТАЦИЯ API РОУТОВ
========================

Сервер запускается на: http://localhost:81

Всего роутов: 12
- Управление направлениями: 1
- Управление тестами: 5 (CRUD операции)
- Управление тест-сессиями: 6

1. РОУТ: GET /directions
   Описание: Получает все направления из MySQL базы данных
   Метод: GET
   Параметры: нет
   Ответ: JSON массив с объектами направлений
   Пример ответа:
   [
     {"id": 1, "name": "Программирование"},
     {"id": 2, "name": "Дизайн"}
   ]

2. РОУТ: GET /tests/<direction>
   Описание: Получает список тестов по названию направления из MongoDB
   Метод: GET
   Параметры: 
   - direction (в URL) - название направления (например: "Программирование")
   Ответ: JSON массив с объектами тестов
   Пример запроса: GET /tests/Программирование
   Пример ответа:
   [
     {
       "id": "68b8506b0bb37f22653b3550",
       "title": "Основы Python для начинающих",
       "startDate": "2023-11-10T00:00:00Z",
       "endDate": "2023-12-10T23:59:00Z",
       "timeLimitMinutes": 25
     }
   ]

3. РОУТ: GET /test/<test_id>
   Описание: Получает полный тест по его ID из MongoDB
   Метод: GET
   Параметры:
   - test_id (в URL) - ID теста (например: "68b8506b0bb37f22653b3550")
   Ответ: JSON объект с полными данными теста
   Пример запроса: GET /test/68b8506b0bb37f22653b3550
   Пример ответа:
   {
     "_id": "68b8506b0bb37f22653b3550",
     "title": "Основы Python для начинающих",
     "direction": "Программирование",
     "startDate": "2023-11-10T00:00:00Z",
     "endDate": "2023-12-10T23:59:00Z",
     "timeLimitMinutes": 25,
     "questions": [...],
     "createdAt": "2023-11-01T09:45:00Z",
     "updatedAt": "2023-11-15T14:30:00Z",
     "isActive": true
   }
   Ошибка 404: {"error": "Test not found"}

4. РОУТ: POST /create-test
   Описание: Создает новый тест в MongoDB
   Метод: POST
   Параметры: JSON объект в теле запроса
   Заголовки: Content-Type: application/json
   Пример запроса:
   POST /create-test
   Content-Type: application/json
   {
     "title": "Новый тест по Python",
     "direction": "Программирование",
     "startDate": "2024-01-15T00:00:00Z",
     "endDate": "2024-02-15T23:59:00Z",
     "timeLimitMinutes": 30,
     "questions": [
       {
         "questionId": 1,
         "type": "single",
         "text": "Что такое Python?",
         "points": 5,
         "answers": [
           {"id": "a", "text": "Язык программирования", "isCorrect": true},
           {"id": "b", "text": "Змея", "isCorrect": false}
         ]
       }
     ],
     "isActive": true
   }
   Ответ: JSON объект с ID созданного теста
   Пример ответа: {"id": "68b8506b0bb37f22653b3550"}

5. РОУТ: POST /create-test-session
   Описание: Создает тест-сессию с ответами студента
   Метод: POST
   Параметры: JSON объект в теле запроса
   Заголовки: Content-Type: application/json
   Пример запроса:
   POST /create-test-session
   Content-Type: application/json
   {
     "studentId": "6",
     "testId": "68b8506b0bb37f22653b3550",
     "testTitle": "Название теста",
     "answers": [
       {
         "questionId": 1,
         "type": "single",
         "selectedAnswer": "a",
         "isCorrect": true,
         "points": 5
       }
     ],
     "timeSpentMinutes": 30
   }
   Ответ: JSON объект с ID созданной сессии
   Пример ответа: {"id": "68d27eacb8cf13957f488dbf"}

6. РОУТ: GET /test-session/<session_id>
   Описание: Получает тест-сессию по ID
   Метод: GET
   Параметры:
   - session_id (в URL) - ID тест-сессии
   Ответ: JSON объект с данными сессии
   Ошибка 404: {"error": "Test session not found"}

7. РОУТ: GET /test-session/<session_id>/stats
   Описание: Получает детальную статистику по тест-сессии
   Метод: GET
   Параметры:
   - session_id (в URL) - ID тест-сессии
   Ответ: JSON объект со статистикой
   Пример ответа:
   {
     "sessionId": "68d27eacb8cf13957f488dbf",
     "studentId": "6",
     "testTitle": "Название теста",
     "totalQuestions": 4,
     "correctAnswers": 4,
     "accuracy": 100.0,
     "totalPoints": 25,
     "timeSpentMinutes": 18,
     "questionTypes": {...},
     "answers": [...]
   }
   Ошибка 404: {"error": "Test session not found"}

8. РОУТ: GET /test-sessions/student/<student_id>
   Описание: Получает все тест-сессии студента
   Метод: GET
   Параметры:
   - student_id (в URL) - ID студента
   Ответ: JSON массив с сессиями студента

9. РОУТ: GET /test-sessions/test/<test_id>
   Описание: Получает все тест-сессии по тесту
   Метод: GET
   Параметры:
   - test_id (в URL) - ID теста
   Ответ: JSON массив с сессиями по тесту

10. РОУТ: GET /test-session/student/<student_id>/test/<test_id>
    Описание: Получает конкретную тест-сессию по студенту и тесту
    Метод: GET
    Параметры:
    - student_id (в URL) - ID студента
    - test_id (в URL) - ID теста
    Ответ: JSON объект с данными сессии
    Ошибка 404: {"error": "Test session not found"}

11. РОУТ: PUT /test/<test_id>
    Описание: Обновляет существующий тест
    Метод: PUT
    Параметры: JSON объект в теле запроса
    Заголовки: Content-Type: application/json
    Пример запроса:
    PUT /test/68b8506b0bb37f22653b3550
    Content-Type: application/json
    {
      "title": "Обновленное название теста",
      "direction": "Математика",
      "startDate": "2024-01-15T00:00:00Z",
      "endDate": "2024-02-15T23:59:00Z",
      "timeLimitMinutes": 45,
      "questions": [...],
      "isActive": true
    }
    Ответ: JSON объект с подтверждением обновления И статистикой пересчета сессий
    Пример ответа:
    {
      "message": "Test updated successfully",
      "testId": "68b8506b0bb37f22653b3550",
      "recalc": {"sessions": 12, "updated": 12}
    }
    Ошибка 404: {"error": "Test not found"}
    Ошибка 500: {"error": "Failed to update test"}

12. РОУТ: DELETE /test/<test_id>
    Описание: Удаляет тест и все связанные с ним тест-сессии
    Метод: DELETE
    Параметры:
    - test_id (в URL) - ID теста для удаления
    Ответ: JSON объект с результатом удаления
    Пример ответа:
    {
      "message": "Test and related sessions deleted successfully",
      "testId": "68b8506b0bb37f22653b3550",
      "deletedSessions": 3,
      "totalDeleted": 4
    }
    Ошибка 404: {"error": "Test not found"}

СТРУКТУРА ВОПРОСОВ В ТЕСТЕ:
===========================

1. Одиночный выбор (single):
   {
     "questionId": 1,
     "type": "single",
     "text": "Текст вопроса",
     "points": 5,
     "answers": [
       {"id": "a", "text": "Вариант A", "isCorrect": true},
       {"id": "b", "text": "Вариант B", "isCorrect": false}
     ]
   }

2. Множественный выбор (multiple):
   {
     "questionId": 2,
     "type": "multiple",
     "text": "Текст вопроса",
     "points": 10,
     "answers": [
       {"id": "a", "text": "Вариант A", "isCorrect": true, "pointValue": 5},
       {"id": "b", "text": "Вариант B", "isCorrect": true, "pointValue": 5},
       {"id": "c", "text": "Вариант C", "isCorrect": false, "pointValue": 0}
     ]
   }

3. Текстовый ответ (text):
   {
     "questionId": 3,
     "type": "text",
     "text": "Текст вопроса",
     "points": 5,
     "correctAnswers": ["правильный ответ", "альтернативный ответ"]
   }

ОПЕРАЦИИ CRUD ДЛЯ ТЕСТОВ:
=========================

CREATE (Создание):
- POST /create-test - создание нового теста

READ (Чтение):
- GET /directions - получение всех направлений
- GET /tests/<direction> - получение тестов по направлению
- GET /test/<test_id> - получение конкретного теста

UPDATE (Обновление):
- PUT /test/<test_id> - редактирование существующего теста

DELETE (Удаление):
- DELETE /test/<test_id> - удаление теста и всех связанных сессий

ВАЖНЫЕ ОСОБЕННОСТИ:
==================

1. При редактировании теста автоматически добавляется поле "updatedAt"
2. При удалении теста каскадно удаляются все связанные тест-сессии
3. Все операции проверяют существование теста перед выполнением
4. Невалидные ObjectId корректно обрабатываются (возвращают 404)

СТРУКТУРА ОТВЕТОВ В ТЕСТ-СЕССИИ:
================================

1. Ответ на вопрос с одиночным выбором:
   {
     "questionId": 1,
     "type": "single",
     "selectedAnswer": "a",
     "isCorrect": true,
     "points": 5
   }

2. Ответ на вопрос с множественным выбором:
   {
     "questionId": 2,
     "type": "multiple",
     "selectedAnswers": ["a", "c"],
     "isCorrect": true,
     "points": 10
   }

3. Ответ на текстовый вопрос:
   {
     "questionId": 3,
     "type": "text",
     "textAnswer": "правильный ответ",
     "isCorrect": true,
     "points": 5
   }

ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
======================

1. Получить все направления:
   curl http://localhost:81/directions

2. Получить тесты по направлению:
   curl http://localhost:81/tests/Программирование

3. Получить конкретный тест:
   curl http://localhost:81/test/68b8506b0bb37f22653b3550

4. Создать новый тест:
   curl -X POST http://localhost:81/create-test \
   -H "Content-Type: application/json" \
   -d '{"title": "Тест", "direction": "Программирование", ...}'

5. Создать тест-сессию:
   curl -X POST http://localhost:81/create-test-session \
   -H "Content-Type: application/json" \
   -d '{"studentId": "6", "testId": "68b8506b0bb37f22653b3550", ...}'

6. Получить тест-сессию по ID:
   curl http://localhost:81/test-session/68d27eacb8cf13957f488dbf

7. Получить статистику сессии:
   curl http://localhost:81/test-session/68d27eacb8cf13957f488dbf/stats

8. Получить все сессии студента:
   curl http://localhost:81/test-sessions/student/6

9. Получить все сессии по тесту:
   curl http://localhost:81/test-sessions/test/68b8506b0bb37f22653b3550

10. Найти сессию студента по конкретному тесту:
    curl http://localhost:81/test-session/student/6/test/68b8506b0bb37f22653b3550

11. Редактировать тест:
    curl -X PUT http://localhost:81/test/68b8506b0bb37f22653b3550 \
    -H "Content-Type: application/json" \
    -d '{"title": "Новое название", "direction": "Математика", ...}'

12. Удалить тест и все его сессии:
    curl -X DELETE http://localhost:81/test/68b8506b0bb37f22653b3550

БАЗЫ ДАННЫХ:
============

MySQL (направления):
- Хост: 147.45.138.77:3306
- База: minishep
- Таблица: directions

MongoDB (тесты и сессии):
- Хост: 109.73.202.73:27017
- База: default_db
- Коллекции:
  - tests - тесты и вопросы
  - test_sessions - тест-сессии с ответами студентов
