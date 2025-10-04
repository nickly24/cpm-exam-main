#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для быстрого запуска тестов производительности
"""

import subprocess
import sys
import os

def install_requirements():
    """Устанавливает необходимые зависимости"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"])
        print("✅ Зависимости установлены успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        return False

def run_quick_test():
    """Запускает быстрый тест производительности"""
    print("🚀 Запуск быстрого теста производительности...")
    try:
        subprocess.run([sys.executable, "performance_test.py", "--mode", "single", "--concurrent", "5", "--duration", "10"])
    except Exception as e:
        print(f"❌ Ошибка при запуске теста: {e}")

def run_full_test():
    """Запускает полный набор тестов"""
    print("🚀 Запуск полного тестирования производительности...")
    try:
        subprocess.run([sys.executable, "performance_test.py", "--mode", "all", "--save"])
    except Exception as e:
        print(f"❌ Ошибка при запуске теста: {e}")

def main():
    print("🎯 Тестирование производительности API сервера")
    print("="*50)
    
    # Проверяем, установлены ли зависимости
    try:
        import requests
        print("✅ Зависимости уже установлены")
    except ImportError:
        if not install_requirements():
            return
    
    print("\nВыберите тип тестирования:")
    print("1. Быстрый тест (5 одновременных запросов, 10 секунд)")
    print("2. Полный тест (все виды нагрузки)")
    print("3. Выход")
    
    choice = input("\nВведите номер (1-3): ").strip()
    
    if choice == "1":
        run_quick_test()
    elif choice == "2":
        run_full_test()
    elif choice == "3":
        print("👋 До свидания!")
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
