"""
Модуль для сохранения рейтингов в базы данных
"""

import mysql.connector
from pymongo import MongoClient
from datetime import datetime
from db import db

# Настройки подключения к MongoDB
MONGODB_URI = 'mongodb://gen_user:I_OBNu~9oHF0(m@81.200.148.71:27017/default_db?authSource=admin&directConnection=true'


def save_rating_to_mysql(mysql_conn, rating_data):
    """
    Сохраняет рейтинг в таблицу Allratings в MySQL
    
    Args:
        mysql_conn: соединение с MySQL
        rating_data: данные рейтинга от calculate_student_rating
    
    Returns:
        dict: {'success': bool, 'rating_id': int, 'message': str}
    """
    cursor = mysql_conn.cursor(dictionary=True)
    
    try:
        # Проверяем, существует ли запись для этого студента
        check_query = "SELECT id FROM Allratings WHERE student_id = %s"
        cursor.execute(check_query, (rating_data['student_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # Обновляем существующую запись
            update_query = """
                UPDATE Allratings 
                SET exams = %s, homework = %s, tests = %s, final = %s
                WHERE student_id = %s
            """
            cursor.execute(update_query, (
                float(rating_data['exams']['rating']),
                float(rating_data['homework']['rating']),
                float(rating_data['tests']['rating']),
                float(rating_data['final_rating']),
                rating_data['student_id']
            ))
            rating_id = existing['id']
            mysql_conn.commit()
            return {
                'success': True,
                'rating_id': rating_id,
                'message': 'Рейтинг обновлен',
                'is_new': False
            }
        else:
            # Создаем новую запись
            insert_query = """
                INSERT INTO Allratings (student_id, exams, homework, tests, final)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                rating_data['student_id'],
                float(rating_data['exams']['rating']),
                float(rating_data['homework']['rating']),
                float(rating_data['tests']['rating']),
                float(rating_data['final_rating'])
            ))
            rating_id = cursor.lastrowid
            mysql_conn.commit()
            return {
                'success': True,
                'rating_id': rating_id,
                'message': 'Рейтинг создан',
                'is_new': True
            }
            
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        return {
            'success': False,
            'rating_id': None,
            'message': f'Ошибка MySQL: {str(e)}',
            'is_new': False
        }
    finally:
        cursor.close()


def save_rating_details_to_mongo(mongo_client, rating_id, rating_data):
    """
    Сохраняет детализацию рейтинга в MongoDB коллекцию rate_rec
    
    Args:
        mongo_client: клиент MongoDB
        rating_id: ID записи из MySQL Allratings
        rating_data: данные рейтинга от calculate_student_rating
    
    Returns:
        dict: {'success': bool, 'mongo_id': str, 'message': str}
    """
    db = mongo_client.default_db
    rate_rec_collection = db.rate_rec
    
    try:
        # Формируем документ для MongoDB
        mongo_doc = {
            'rating_id': rating_id,  # ID из MySQL
            'student_id': rating_data['student_id'],
            'date_from': rating_data['date_from'],
            'date_to': rating_data['date_to'],
            'calculated_at': datetime.utcnow().isoformat() + 'Z',
            'homework': {
                'rating': rating_data['homework']['rating'],
                'details': rating_data['homework']['details']
            },
            'exams': {
                'rating': rating_data['exams']['rating'],
                'details': rating_data['exams']['details']
            },
            'tests': {
                'rating': rating_data['tests']['rating'],
                'directions': rating_data['tests']['directions'],
                'details': rating_data['tests']['details']
            },
            'final_rating': rating_data['final_rating']
        }
        
        # Проверяем, существует ли запись
        existing = rate_rec_collection.find_one({'rating_id': rating_id})
        
        if existing:
            # Обновляем существующую запись
            result = rate_rec_collection.update_one(
                {'rating_id': rating_id},
                {'$set': mongo_doc}
            )
            return {
                'success': True,
                'mongo_id': str(existing['_id']),
                'message': 'Детализация обновлена',
                'is_new': False
            }
        else:
            # Создаем новую запись
            result = rate_rec_collection.insert_one(mongo_doc)
            return {
                'success': True,
                'mongo_id': str(result.inserted_id),
                'message': 'Детализация создана',
                'is_new': True
            }
            
    except Exception as e:
        return {
            'success': False,
            'mongo_id': None,
            'message': f'Ошибка MongoDB: {str(e)}',
            'is_new': False
        }


def clear_all_ratings(mysql_conn, mongo_client):
    """
    Очищает все рейтинги из MySQL и MongoDB
    
    Args:
        mysql_conn: соединение с MySQL
        mongo_client: клиент MongoDB
    
    Returns:
        dict: результат очистки
    """
    mysql_success = False
    mongo_success = False
    mysql_error = None
    mongo_error = None
    
    # Очищаем MySQL
    try:
        cursor = mysql_conn.cursor()
        cursor.execute("DELETE FROM Allratings")
        mysql_conn.commit()
        cursor.close()
        mysql_success = True
    except Exception as e:
        mysql_conn.rollback()
        mysql_error = str(e)
    
    # Очищаем MongoDB
    try:
        db = mongo_client.default_db
        rate_rec_collection = db.rate_rec
        rate_rec_collection.delete_many({})
        mongo_success = True
    except Exception as e:
        mongo_error = str(e)
    
    return {
        'mysql_success': mysql_success,
        'mongo_success': mongo_success,
        'mysql_error': mysql_error,
        'mongo_error': mongo_error
    }


def check_student_exists(mysql_conn, student_id):
    """
    Проверяет существование студента в базе данных
    
    Args:
        mysql_conn: соединение с MySQL
        student_id: ID студента
    
    Returns:
        bool: True если студент существует, False иначе
    """
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None


def save_all_ratings(mysql_conn, mongo_client, date_from, date_to):
    """
    Рассчитывает и сохраняет рейтинги для всех актуальных студентов
    Перед расчетом очищает все существующие рейтинги
    
    Args:
        mysql_conn: соединение с MySQL
        mongo_client: клиент MongoDB
        date_from: начальная дата (YYYY-MM-DD)
        date_to: конечная дата (YYYY-MM-DD)
    
    Returns:
        dict: статистика обработки
    """
    from calculate_ratings import calculate_student_rating
    
    # Очищаем все существующие рейтинги
    clear_result = clear_all_ratings(mysql_conn, mongo_client)
    
    if not clear_result['mysql_success']:
        return {
            'total_students': 0,
            'successful': 0,
            'failed': 0,
            'errors': [f"Ошибка очистки MySQL: {clear_result['mysql_error']}"],
            'clear_error': True
        }
    
    if not clear_result['mongo_success']:
        return {
            'total_students': 0,
            'successful': 0,
            'failed': 0,
            'errors': [f"Ошибка очистки MongoDB: {clear_result['mongo_error']}"],
            'clear_error': True
        }
    
    # Получаем список актуальных студентов
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM students ORDER BY id")
    students = cursor.fetchall()
    cursor.close()
    
    results = {
        'total_students': len(students),
        'successful': 0,
        'failed': 0,
        'errors': [],
        'skipped': 0
    }
    
    for student in students:
        student_id = student['id']
        
        # Проверяем существование студента перед расчетом
        if not check_student_exists(mysql_conn, student_id):
            results['skipped'] += 1
            results['errors'].append({
                'student_id': student_id,
                'error': 'Студент не найден в базе данных'
            })
            continue
        
        try:
            # Рассчитываем рейтинг
            rating_data = calculate_student_rating(
                mysql_conn, mongo_client, student_id, date_from, date_to
            )
            
            # Сохраняем в MySQL
            mysql_result = save_rating_to_mysql(mysql_conn, rating_data)
            
            if mysql_result['success']:
                # Сохраняем детализацию в MongoDB
                mongo_result = save_rating_details_to_mongo(
                    mongo_client, mysql_result['rating_id'], rating_data
                )
                
                if mongo_result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'student_id': student_id,
                        'error': f"MongoDB: {mongo_result['message']}"
                    })
            else:
                results['failed'] += 1
                results['errors'].append({
                    'student_id': student_id,
                    'error': f"MySQL: {mysql_result['message']}"
                })
                
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'student_id': student_id,
                'error': f"Расчет: {str(e)}"
            })
    
    return results

