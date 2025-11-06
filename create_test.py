from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

client = MongoClient('mongodb://gen_user:I_OBNu~9oHF0(m@81.200.148.71:27017/default_db?authSource=admin&directConnection=true')

def create_test(test_data):
    db = client.default_db
    tests_collection = db.tests
    
    test_data["createdAt"] = datetime.utcnow().isoformat() + "Z"
    
    result = tests_collection.insert_one(test_data)
    
    return str(result.inserted_id)

def update_test(test_id, test_data):
    """
    Обновляет существующий тест
    
    Args:
        test_id (str): ID теста для обновления
        test_data (dict): Новые данные теста
    
    Returns:
        bool: True если тест обновлен, False если не найден
    """
    db = client.default_db
    tests_collection = db.tests
    
    # Добавляем время обновления
    test_data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    
    result = tests_collection.update_one(
        {"_id": ObjectId(test_id)},
        {"$set": test_data}
    )
    
    return result.modified_count > 0

def delete_test(test_id):
    """
    Удаляет тест и все связанные с ним тест-сессии
    
    Args:
        test_id (str): ID теста для удаления
    
    Returns:
        dict: Результат удаления с количеством удаленных записей
    """
    db = client.default_db
    tests_collection = db.tests
    test_sessions_collection = db.test_sessions
    
    # Сначала удаляем все тест-сессии этого теста
    sessions_result = test_sessions_collection.delete_many({"testId": test_id})
    sessions_deleted = sessions_result.deleted_count
    
    # Затем удаляем сам тест
    test_result = tests_collection.delete_one({"_id": ObjectId(test_id)})
    test_deleted = test_result.deleted_count
    
    return {
        "test_deleted": test_deleted > 0,
        "sessions_deleted": sessions_deleted,
        "total_deleted": test_deleted + sessions_deleted
    }

def get_test_by_id(test_id):
    """
    Получает тест по ID
    
    Args:
        test_id (str): ID теста
    
    Returns:
        dict: Данные теста или None
    """
    try:
        db = client.default_db
        tests_collection = db.tests
        
        test = tests_collection.find_one({"_id": ObjectId(test_id)})
        
        if test:
            test["_id"] = str(test["_id"])
            return test
        
        return None
    except Exception:
        # Если ObjectId невалидный, возвращаем None
        return None
