#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест подключения к Supabase с вашим ключом
"""

import os
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
                os.environ[key] = value
                print(f"   ✅ {key}: {'*' * min(len(value), 20)}...")
    
    return True


def test_supabase():
    """Тест подключения к Supabase"""
    try:
        from supabase import create_client
        
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL или SUPABASE_KEY не настроены!")
            return False
        
        print(f"\n🔄 Тестирование подключения к Supabase...")
        print(f"URL: {supabase_url}")
        print(f"Key: {supabase_key[:20]}...")
        
        # Создаем клиент
        supabase = create_client(supabase_url, supabase_key)
        
        # Тестируем подключение
        result = supabase.table('tinkoff_operations').select('*').limit(1).execute()
        
        print("✅ Подключение к Supabase успешно!")
        print(f"📊 Найдено записей в таблице: {len(result.data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        return False


def main():
    """Основная функция"""
    print("🧪 ТЕСТ ПОДКЛЮЧЕНИЯ К SUPABASE")
    print("="*50)
    
    # Загружаем переменные из файла
    if not load_env_from_file():
        return
    
    print("\n" + "="*50)
    
    # Тестируем Supabase
    if test_supabase():
        print("\n🎉 Supabase готов к работе!")
        print("💡 Теперь можно запускать:")
        print("   python3 tinkoff_to_supabase.py")
    else:
        print("\n⚠️ Проблема с подключением к Supabase")
        print("🔧 Проверьте ключ и URL")


if __name__ == "__main__":
    main()
