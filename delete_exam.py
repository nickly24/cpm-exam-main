from db import db
import mysql.connector

def delete_exam(exam_id):
    connection = mysql.connector.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        db=db.db
    )
    cursor = connection.cursor()
    
    try:
        # SQL-запрос для удаления записи
        query = "DELETE FROM exams WHERE id = %s"
        cursor.execute(query, (exam_id,))
        
        # Подтверждаем изменения в базе данных
        connection.commit()
        
        # Проверяем, была ли удалена хотя бы одна запись
        if cursor.rowcount > 0:
            return True  # Успешное удаление
        else:
            return False  # Запись с таким ID не найдена
            
    except mysql.connector.Error as error:
        # В случае ошибки откатываем изменения
        connection.rollback()
        print(f"Ошибка при удалении записи: {error}")
        return False
        
    finally:
        # Закрываем соединение в любом случае
        if connection.is_connected():
            cursor.close()
            connection.close()