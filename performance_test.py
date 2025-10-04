#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования производительности API сервера
Тестирует различные эндпоинты с разной нагрузкой
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from typing import List, Dict, Any
import argparse

class PerformanceTester:
    def __init__(self, base_url: str = "https://nickly24-cpm-exam-main-225a.twc1.net"):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Тестирует один эндпоинт и возвращает метрики"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, timeout=30)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # в миллисекундах
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": 200 <= response.status_code < 300,
                "timestamp": datetime.now().isoformat(),
                "response_size_bytes": len(response.content)
            }
            
            # Добавляем информацию об ошибках
            if not result["success"]:
                result["error"] = response.text[:200]  # Первые 200 символов ошибки
                
            return result
            
        except requests.exceptions.Timeout:
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time_ms": 30000,  # 30 секунд таймаут
                "success": False,
                "error": "Timeout (30s)",
                "timestamp": datetime.now().isoformat(),
                "response_size_bytes": 0
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time_ms": 0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "response_size_bytes": 0
            }
    
    def test_single_load(self, concurrent_requests: int = 1, duration_seconds: int = 10) -> Dict[str, Any]:
        """Тестирует нагрузку с заданным количеством одновременных запросов"""
        print(f"\n🚀 Тестирование нагрузки: {concurrent_requests} одновременных запросов в течение {duration_seconds} секунд")
        
        # Определяем эндпоинты для тестирования
        endpoints_to_test = [
            "/",
            "/directions", 
            "/tests/informatika",  # Предполагаем, что есть такое направление
            "/tests/matematika",   # И такое тоже
        ]
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            while time.time() < end_time:
                for endpoint in endpoints_to_test:
                    future = executor.submit(self.test_endpoint, endpoint)
                    futures.append(future)
                    
                    # Небольшая задержка между отправкой запросов
                    time.sleep(0.1)
            
            # Собираем результаты
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=35)  # Немного больше таймаута запроса
                    results.append(result)
                except Exception as e:
                    print(f"Ошибка при получении результата: {e}")
        
        return self.analyze_results(results, concurrent_requests, duration_seconds)
    
    def test_gradual_load(self, max_concurrent: int = 50, step: int = 5) -> List[Dict[str, Any]]:
        """Тестирует постепенно увеличивающуюся нагрузку"""
        print(f"\n📈 Тестирование постепенной нагрузки от 1 до {max_concurrent} одновременных запросов")
        
        all_results = []
        
        for concurrent in range(1, max_concurrent + 1, step):
            print(f"\n--- Тестирование с {concurrent} одновременными запросами ---")
            result = self.test_single_load(concurrent, duration_seconds=5)
            result["concurrent_requests"] = concurrent
            all_results.append(result)
            
            # Небольшая пауза между тестами
            time.sleep(2)
        
        return all_results
    
    def test_burst_load(self, burst_size: int = 100, duration_seconds: int = 5) -> Dict[str, Any]:
        """Тестирует кратковременную высокую нагрузку (burst)"""
        print(f"\n💥 Тестирование кратковременной нагрузки: {burst_size} запросов за {duration_seconds} секунд")
        
        endpoints = ["/", "/directions", "/tests/informatika"]
        results = []
        
        with ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = []
            
            # Отправляем все запросы практически одновременно
            for i in range(burst_size):
                endpoint = endpoints[i % len(endpoints)]
                future = executor.submit(self.test_endpoint, endpoint)
                futures.append(future)
            
            # Собираем результаты
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=35)
                    results.append(result)
                except Exception as e:
                    print(f"Ошибка при получении результата: {e}")
        
        return self.analyze_results(results, burst_size, duration_seconds)
    
    def analyze_results(self, results: List[Dict], concurrent_requests: int, duration: int) -> Dict[str, Any]:
        """Анализирует результаты тестирования и возвращает статистику"""
        if not results:
            return {"error": "Нет результатов для анализа"}
        
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        response_times = [r["response_time_ms"] for r in successful_requests]
        
        analysis = {
            "concurrent_requests": concurrent_requests,
            "test_duration_seconds": duration,
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate_percent": (len(successful_requests) / len(results)) * 100 if results else 0,
            "requests_per_second": len(results) / duration if duration > 0 else 0,
        }
        
        if response_times:
            analysis.update({
                "avg_response_time_ms": statistics.mean(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "median_response_time_ms": statistics.median(response_times),
                "p95_response_time_ms": self.percentile(response_times, 95),
                "p99_response_time_ms": self.percentile(response_times, 99),
            })
        
        # Группировка ошибок
        error_summary = {}
        for req in failed_requests:
            error_type = req.get("error", "Unknown error")
            if error_type in error_summary:
                error_summary[error_type] += 1
            else:
                error_summary[error_type] = 1
        
        analysis["error_summary"] = error_summary
        
        return analysis
    
    def percentile(self, data: List[float], percentile: float) -> float:
        """Вычисляет перцентиль"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def print_results(self, results: Dict[str, Any]):
        """Красиво выводит результаты тестирования"""
        print("\n" + "="*60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("="*60)
        
        print(f"\n🔄 Параметры теста:")
        print(f"   • Одновременные запросы: {results.get('concurrent_requests', 'N/A')}")
        print(f"   • Длительность теста: {results.get('test_duration_seconds', 'N/A')} сек")
        
        print(f"\n📈 Общая статистика:")
        print(f"   • Всего запросов: {results.get('total_requests', 0)}")
        print(f"   • Успешных запросов: {results.get('successful_requests', 0)}")
        print(f"   • Неудачных запросов: {results.get('failed_requests', 0)}")
        print(f"   • Процент успеха: {results.get('success_rate_percent', 0):.1f}%")
        print(f"   • Запросов в секунду: {results.get('requests_per_second', 0):.1f}")
        
        if 'avg_response_time_ms' in results:
            print(f"\n⏱️  Время ответа:")
            print(f"   • Среднее: {results['avg_response_time_ms']:.1f} мс")
            print(f"   • Минимальное: {results['min_response_time_ms']:.1f} мс")
            print(f"   • Максимальное: {results['max_response_time_ms']:.1f} мс")
            print(f"   • Медиана: {results['median_response_time_ms']:.1f} мс")
            print(f"   • 95-й перцентиль: {results['p95_response_time_ms']:.1f} мс")
            print(f"   • 99-й перцентиль: {results['p99_response_time_ms']:.1f} мс")
        
        if results.get('error_summary'):
            print(f"\n❌ Ошибки:")
            for error, count in results['error_summary'].items():
                print(f"   • {error}: {count}")
        
        print("="*60)
    
    def save_results_to_file(self, results: List[Dict], filename: str = None):
        """Сохраняет результаты в JSON файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в файл: {filename}")


def main():
    parser = argparse.ArgumentParser(description='Тестирование производительности API сервера')
    parser.add_argument('--url', default='https://nickly24-cpm-exam-main-225a.twc1.net', 
                       help='Базовый URL сервера')
    parser.add_argument('--mode', choices=['single', 'gradual', 'burst', 'all'], default='all',
                       help='Режим тестирования')
    parser.add_argument('--concurrent', type=int, default=10,
                       help='Количество одновременных запросов (для single режима)')
    parser.add_argument('--duration', type=int, default=10,
                       help='Длительность теста в секундах')
    parser.add_argument('--max-concurrent', type=int, default=50,
                       help='Максимальное количество одновременных запросов (для gradual режима)')
    parser.add_argument('--burst-size', type=int, default=100,
                       help='Размер кратковременной нагрузки (для burst режима)')
    parser.add_argument('--save', action='store_true',
                       help='Сохранить результаты в файл')
    
    args = parser.parse_args()
    
    print("🚀 Запуск тестирования производительности API сервера")
    print(f"🌐 URL: {args.url}")
    
    tester = PerformanceTester(args.url)
    all_results = []
    
    try:
        if args.mode in ['single', 'all']:
            print("\n" + "="*50)
            print("🔍 ТЕСТ 1: Одиночная нагрузка")
            print("="*50)
            result = tester.test_single_load(args.concurrent, args.duration)
            tester.print_results(result)
            all_results.append({"test_type": "single_load", "result": result})
        
        if args.mode in ['gradual', 'all']:
            print("\n" + "="*50)
            print("📈 ТЕСТ 2: Постепенно увеличивающаяся нагрузка")
            print("="*50)
            gradual_results = tester.test_gradual_load(args.max_concurrent, step=5)
            for result in gradual_results:
                tester.print_results(result)
            all_results.append({"test_type": "gradual_load", "results": gradual_results})
        
        if args.mode in ['burst', 'all']:
            print("\n" + "="*50)
            print("💥 ТЕСТ 3: Кратковременная высокая нагрузка")
            print("="*50)
            burst_result = tester.test_burst_load(args.burst_size, 5)
            tester.print_results(burst_result)
            all_results.append({"test_type": "burst_load", "result": burst_result})
        
        if args.save:
            tester.save_results_to_file(all_results)
        
        print("\n✅ Тестирование завершено!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")


if __name__ == "__main__":
    main()
