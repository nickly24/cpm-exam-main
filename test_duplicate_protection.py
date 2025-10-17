#!/usr/bin/env python3
"""
Тестовый скрипт для проверки защиты от дублирования тест-сессий
"""

import requests
import json
import time

# URL API
API_URL = "http://localhost:81"

def test_duplicate_protection():
    """Тестирует защиту от дублирования тест-сессий"""
    
    # Тестовые данные
    test_data = {
        "studentId": "test_student_123",
        "testId": "test_id_456", 
        "testTitle": "Тестовый тест",
        "answers": [
            {
                "questionId": 1,
                "type": "single",
                "selectedAnswer": "a",
                "points": 1,
                "isCorrect": True
            }
        ],
        "score": 1,
        "timeSpentMinutes": 5
    }
    
    print("🧪 Тестирование защиты от дублирования тест-сессий")
    print("=" * 60)
    
    # Первая попытка создания сессии
    print("1️⃣ Отправляем первую попытку создания тест-сессии...")
    response1 = requests.post(f"{API_URL}/create-test-session", json=test_data)
    
    print(f"Статус код: {response1.status_code}")
    print(f"Ответ: {json.dumps(response1.json(), indent=2, ensure_ascii=False)}")
    
    if response1.status_code == 200:
        print("✅ Первая сессия создана успешно")
    else:
        print("❌ Ошибка при создании первой сессии")
        return
    
    print("\n" + "-" * 40 + "\n")
    
    # Вторая попытка создания сессии (должна быть заблокирована)
    print("2️⃣ Отправляем вторую попытку создания тест-сессии (должна быть заблокирована)...")
    response2 = requests.post(f"{API_URL}/create-test-session", json=test_data)
    
    print(f"Статус код: {response2.status_code}")
    print(f"Ответ: {json.dumps(response2.json(), indent=2, ensure_ascii=False)}")
    
    if response2.status_code == 409:
        print("✅ Дублирование успешно заблокировано!")
        print("🎯 Тест пройден - защита работает корректно")
    else:
        print("❌ ОШИБКА: Дублирование не было заблокировано!")
        print("🚨 Проблема с защитой от дублирования")
    
    print("\n" + "=" * 60)
    print("Тест завершен")

if __name__ == "__main__":
    try:
        test_duplicate_protection()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к серверу")
        print("Убедитесь, что сервер запущен на localhost:81")
    except Exception as e:
        print(f"❌ Ошибка при выполнении теста: {e}")
