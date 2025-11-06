#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для аккуратного пересчета ВСЕХ тест-сессий в БД
ВАЖНО: НЕ изменяет answers, только пересчитывает points, isCorrect, score
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Подключение к MongoDB
client = MongoClient('mongodb://gen_user:I_OBNu~9oHF0(m@81.200.148.71:27017/default_db?authSource=admin&directConnection=true')
db = client.default_db

def normalize_text(value: str) -> str:
    """Нормализация текста для сравнения"""
    if value is None:
        return ""
    return str(value).strip().lower()

def score_single(selected_answer_id: str, question: dict) -> tuple[int, bool]:
    """Правильная логика для единичного выбора"""
    correct_ids = {a.get("id") for a in question.get("answers", []) if a.get("isCorrect")}
    is_correct = selected_answer_id in correct_ids
    points = int(question.get("points", 0)) if is_correct else 0
    return points, is_correct

def score_multiple(selected_answer_ids: list, question: dict) -> tuple[int, bool]:
    """
    Правильная логика для множественного выбора:
    - Должны быть выбраны ВСЕ правильные ответы
    - Не должно быть выбрано НИ ОДНОГО неправильного ответа
    - Иначе - 0 баллов
    """
    total_available = int(question.get("points", 0))
    selected_set = set(selected_answer_ids or [])
    
    # Получаем все правильные ответы
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

def score_text(text_answer: str, question: dict) -> tuple[int, bool]:
    """
    Правильная логика для текстового ответа:
    - Буква в букву (с учетом нормализации)
    - Совпадение с одним из правильных ответов
    """
    normalized = normalize_text(text_answer)
    correct_list = [
        normalize_text(val) for val in (question.get("correctAnswers") or [])
    ]
    is_correct = normalized in correct_list if correct_list else False
    points = int(question.get("points", 0)) if is_correct else 0
    return points, is_correct

def recalc_answer(existing_answer: dict, question: dict) -> dict:
    """Пересчитывает один ответ по правильной логике"""
    a_type = existing_answer.get("type") or question.get("type")
    updated = dict(existing_answer)
    
    if a_type == "single":
        pts, ok = score_single(existing_answer.get("selectedAnswer"), question)
    elif a_type == "multiple":
        pts, ok = score_multiple(existing_answer.get("selectedAnswers", []), question)
    elif a_type == "text":
        pts, ok = score_text(existing_answer.get("textAnswer"), question)
    else:
        pts, ok = 0, False
    
    updated["type"] = a_type
    updated["points"] = int(pts)
    updated["isCorrect"] = bool(ok)
    return updated

def main():
    """Главная функция пересчета"""
    print("=" * 80)
    print("АККУРАТНЫЙ ПЕРЕСЧЕТ ВСЕХ ТЕСТ-СЕССИЙ")
    print("=" * 80)
    print("ВАЖНО: НЕ изменяет answers, только пересчитывает points, isCorrect, score")
    print("=" * 80)
    
    # Получаем все тест-сессии
    print("\n📊 Загружаем тест-сессии из БД...")
    sessions = list(db.test_sessions.find())
    print(f"✅ Найдено {len(sessions)} тест-сессий")
    
    if not sessions:
        print("❌ Тест-сессии не найдены")
        return
    
    # Группируем по тестам для кэширования
    print("\n📋 Группируем сессии по тестам...")
    test_ids = set(s.get("testId") for s in sessions)
    tests_cache = {}
    
    for test_id in test_ids:
        try:
            test = db.tests.find_one({"_id": ObjectId(test_id)})
            if test:
                test["_id"] = str(test["_id"])
                tests_cache[test_id] = test
        except Exception as e:
            print(f"⚠️  Не удалось загрузить тест {test_id}: {e}")
    
    print(f"✅ Загружено {len(tests_cache)} тестов")
    
    # Пересчитываем каждую сессию
    print("\n🔬 Пересчитываем сессии...")
    updated_count = 0
    skipped_count = 0
    
    for i, session in enumerate(sessions, 1):
        if i % 100 == 0:
            print(f"   Обработано {i}/{len(sessions)}...")
        
        test = tests_cache.get(session.get("testId"))
        
        if not test:
            skipped_count += 1
            continue
        
        # Создаем индекс вопросов
        questions = test.get("questions", [])
        question_by_id = {q.get("questionId"): q for q in questions}
        
        # Пересчитываем ответы
        answers = session.get("answers", [])
        new_answers = []
        
        total_points = 0
        for answer in answers:
            qid = answer.get("questionId")
            question = question_by_id.get(qid)
            
            if question:
                # Пересчитываем ответ
                recalculated = recalc_answer(answer, question)
                new_answers.append(recalculated)
                total_points += recalculated.get("points", 0)
            else:
                # Вопрос удален из теста - оставляем как есть с 0 баллов
                answer["points"] = 0
                answer["isCorrect"] = False
                new_answers.append(answer)
        
        # Рассчитываем рейтинговый балл
        max_points = sum(int(q.get("points", 0)) for q in questions)
        if max_points > 0:
            new_score = round((total_points / max_points) * 100, 2)
        else:
            new_score = 0
        
        # Обновляем сессию (ВАЖНО: НЕ изменяем answers, только пересчитываем значения)
        update_doc = {
            "answers": new_answers,
            "score": int(new_score),
        }
        
        result = db.test_sessions.update_one(
            {"_id": session["_id"]},
            {"$set": update_doc}
        )
        
        if result.modified_count:
            updated_count += 1
    
    print(f"\n✅ Пересчет завершен")
    print(f"   Обновлено сессий: {updated_count}")
    print(f"   Пропущено сессий: {skipped_count}")
    
    # Теперь удаляем дубликаты
    print("\n🔍 Ищем дубликаты...")
    duplicates = db.test_sessions.aggregate([
        {
            "$group": {
                "_id": {"studentId": "$studentId", "testId": "$testId"},
                "count": {"$sum": 1},
                "sessionIds": {"$push": "$_id"}
            }
        },
        {"$match": {"count": {"$gt": 1}}}
    ])
    
    duplicate_count = 0
    deleted_count = 0
    
    for dup in duplicates:
        duplicate_count += 1
        session_ids = dup["sessionIds"]
        student_id = dup["_id"]["studentId"]
        test_id = dup["_id"]["testId"]
        
        # Оставляем самую старую сессию, остальные удаляем
        sessions_to_check = list(db.test_sessions.find({"_id": {"$in": session_ids}}))
        sessions_sorted = sorted(sessions_to_check, key=lambda s: s.get("createdAt", ""))
        
        # Оставляем первую (самую старую)
        to_keep = sessions_sorted[0]
        to_delete = sessions_sorted[1:]
        
        print(f"\n   Дубликат для studentId={student_id}, testId={test_id}")
        print(f"   Оставляем сессию: {to_keep['_id']} (created: {to_keep.get('createdAt')})")
        print(f"   Удаляем сессий: {len(to_delete)}")
        
        for s in to_delete:
            db.test_sessions.delete_one({"_id": s["_id"]})
            deleted_count += 1
            print(f"     Удалена сессия: {s['_id']} (created: {s.get('createdAt')})")
    
    print(f"\n✅ Обработка дубликатов завершена")
    print(f"   Найдено дубликатов: {duplicate_count}")
    print(f"   Удалено сессий: {deleted_count}")
    
    print("\n🎉 ВСЁ ГОТОВО!")

if __name__ == "__main__":
    main()
