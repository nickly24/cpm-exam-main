import mysql.connector
from db import db
from datetime import datetime, timedelta, date
import calendar

def get_attendance_by_student(student_id, year_month):
    try:
        connection = mysql.connector.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            password=db.password,
            database=db.db
        )
        cursor = connection.cursor(dictionary=True)

        # Получаем все посещённые даты студента за указанный месяц
        date_pattern = year_month + "%"
        cursor.execute("""
            SELECT date FROM attendance 
            WHERE student_id = %s AND date LIKE %s
        """, (student_id, date_pattern))
        raw_attendance = cursor.fetchall()

        # Преобразуем в set объектов datetime.date для корректного сравнения
        present_dates = {record["date"] for record in raw_attendance}

        # Генерируем все даты месяца
        year, month = map(int, year_month.split("-"))
        _, last_day = calendar.monthrange(year, month)

        full_month_data = []
        for day in range(1, last_day + 1):
            current_date = date(year, month, day)
            full_month_data.append({
                "date": current_date.isoformat(),
                "weekday": current_date.strftime("%A"),
                "was_present": current_date in present_dates
            })

        return {
            "status": True,
            "student_id": student_id,
            "month": year_month,
            "attendance": full_month_data
        }

    except mysql.connector.Error as err:
        return {"status": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()