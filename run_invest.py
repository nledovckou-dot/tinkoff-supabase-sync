#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка переменных окружения из файла и запуск invest.py
"""

import os
import subprocess
import sys


def load_env_from_file(filename='config.env'):
    """Загрузка переменных окружения из файла"""
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден")
        return False
    
    print(f"📄 Загружаем переменные из {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Проверяем, что это не шаблон
                if 'your_' not in value and 'YOUR-' not in value:
                    os.environ[key] = value
                    print(f"   ✅ {key}: {'*' * min(len(value), 20)}...")
                else:
                    print(f"   ⚠️ {key}: шаблон (нужно заменить на реальное значение)")
    
    return True


def check_required_vars():
    """Проверка обязательных переменных"""
    required = ['INVEST_TOKEN', 'YA_ACCESS_KEY', 'YA_SECRET_KEY', 'BUCKET_NAME']
    missing = []
    
    for var in required:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Отсутствуют обязательные переменные: {', '.join(missing)}")
        return False
    
    print("✅ Все обязательные переменные настроены")
    return True


def run_invest_script():
    """Запуск оригинального invest.py"""
    try:
        print("🚀 Запускаем invest.py...")
        result = subprocess.run([sys.executable, 'invest.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print("📤 Вывод скрипта:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ invest.py выполнен успешно!")
        else:
            print(f"❌ invest.py завершился с ошибкой (код: {result.returncode})")
            
    except Exception as e:
        print(f"❌ Ошибка запуска invest.py: {e}")


def main():
    """Основная функция"""
    print("🔄 ЗАПУСК СУЩЕСТВУЮЩЕГО ПРОЕКТА INVEST.PY")
    print("="*60)
    
    # Загружаем переменные из файла
    if not load_env_from_file():
        return
    
    print("\n" + "="*60)
    
    # Проверяем обязательные переменные
    if not check_required_vars():
        print("\n🔧 НАСТРОЙТЕ ПЕРЕМЕННЫЕ В ФАЙЛЕ config.env:")
        print("="*60)
        print("1. INVEST_TOKEN - токен Тинькофф")
        print("2. YA_ACCESS_KEY - ключ Yandex S3")
        print("3. YA_SECRET_KEY - секретный ключ Yandex S3")
        print("4. BUCKET_NAME - имя bucket")
        print("5. SUPABASE_URL - URL Supabase")
        print("6. SUPABASE_KEY - ключ Supabase")
        return
    
    # Запускаем invest.py
    print("\n" + "="*60)
    run_invest_script()
    
    print("\n" + "="*60)
    print("🎯 Готово! Проверьте результаты в:")
    print("• Yandex S3 bucket")
    print("• Google Sheets (если настроен)")
    print("• Supabase (если настроен SUPABASE_KEY)")


if __name__ == "__main__":
    main()
