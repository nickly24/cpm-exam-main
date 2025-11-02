# Настройка JWT авторизации для cpm-exam-main

## Важно!

Для работы общей авторизации между серверами `cpm-serv` и `cpm-exam-main` необходимо:

### 1. Общий секретный ключ

**ОБЯЗАТЕЛЬНО** установите одинаковую переменную окружения `JWT_SECRET_KEY` на обоих серверах!

```bash
# На обоих серверах установите одинаковый ключ
export JWT_SECRET_KEY="ваш-секретный-ключ-здесь"
```

Или в `.env` файле:
```
JWT_SECRET_KEY=ваш-секретный-ключ-здесь
```

**Без этого cookie с одного сервера не будут работать на другом!**

### 2. Работа с cookies между серверами

Если серверы на разных доменах/поддоменах, нужно настроить domain для cookie в `cpm-serv/jwt_auth.py`:

```python
response.set_cookie(
    'auth_token',
    token,
    httponly=True,
    secure=is_production,
    samesite='Lax',
    domain='.cpm-lms.ru',  # Добавить domain для работы на поддоменах
    max_age=JWT_EXPIRATION_HOURS * 3600
)
```

Если оба сервера на одном домене (например, `cpm-lms.ru:80` и `cpm-lms.ru:81`), cookie будет работать автоматически.

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Проверка

После настройки проверьте, что cookie с авторизацией работает на обоих серверах:

```bash
# Авторизуйтесь на cpm-serv
curl -X POST http://localhost:80/api/auth \
  -H "Content-Type: application/json" \
  -d '{"login":"your_login","password":"your_password"}' \
  -c cookies.txt

# Проверьте доступ на cpm-exam-main с тем же cookie
curl -X GET http://localhost:81/test-sessions/student/906 \
  -b cookies.txt
```

## Применённые декораторы

Все роуты защищены согласно требованиям:
- `/test/<test_id>` - требуется авторизация
- `/create-test` - только админ
- `/test/<test_id>` PUT/DELETE - только админ
- `/create-test-session` - студент с проверкой ID или админ
- `/test-session/<session_id>` - студент владелец или админ
- `/test-sessions/student/<student_id>` - студент с проверкой ID или админ
- `/test-sessions/test/<test_id>` - только админ
- `/test-session/<session_id>/stats` - студент владелец или админ
- `/test-session/student/<student_id>/test/<test_id>` - студент с проверкой ID или админ
- `/get-attendance` - студент с проверкой ID или админ
- `/get-exam-session` - студент с проверкой ID или админ
- `/get-student-exam-sessions/<student_id>` - студент с проверкой ID или админ
- `/get-all-exam-sessions` - только админ
- `/get-exam-sessions/<exam_id>` - только админ

Роуты без авторизации:
- `/directions` - БЕЗ АВТОРИЗАЦИИ
- `/tests/<direction>` - БЕЗ АВТОРИЗАЦИИ
- `/get-all-exams` - БЕЗ АВТОРИЗАЦИИ

