from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://gen_user:77tanufe@109.73.202.73:27017/default_db?authSource=admin&directConnection=true')

def get_tests_by_direction(direction_name):
    db = client.default_db
    tests_collection = db.tests
    
    tests = tests_collection.find(
        {"direction": direction_name},
        {"_id": 1, "title": 1, "startDate": 1, "endDate": 1, "timeLimitMinutes": 1}
    )
    
    result = []
    for test in tests:
        result.append({
            "id": str(test["_id"]),
            "title": test["title"],
            "startDate": test["startDate"],
            "endDate": test["endDate"],
            "timeLimitMinutes": test["timeLimitMinutes"]
        })
    
    return result

def get_test_by_id(test_id):
    db = client.default_db
    tests_collection = db.tests
    
    test = tests_collection.find_one({"_id": ObjectId(test_id)})
    
    if test:
        test["_id"] = str(test["_id"])
        return test
    
    return None

