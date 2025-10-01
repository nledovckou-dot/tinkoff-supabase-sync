#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой запуск invest.py с загрузкой переменных из config.env
"""

import os
import subprocess
import sys


def load_env_from_file(filename='config.env'):
    """Загрузка переменных окружения из файла"""
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден")
        return False
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value
    
    return True


def main():
    """Основная функция"""
    print("🚀 ЗАПУСК INVEST.PY С ПЕРЕМЕННЫМИ ИЗ CONFIG.ENV")
    print("="*60)
    
    # Загружаем переменные из файла
    if not load_env_from_file():
        return
    
    print("✅ Переменные окружения загружены")
    
    # Запускаем invest.py
    try:
        print("🔄 Запускаем invest.py...")
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


if __name__ == "__main__":
    main()