#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки подключения к Supabase
"""

import os
import logging
from supabase import create_client, Client


def test_supabase_connection():
    """Тестирование подключения к Supabase"""
    try:
        # Получаем переменные окружения
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Переменные SUPABASE_URL и SUPABASE_KEY не настроены")
            return False
        
        # Создаем клиент
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Тестируем подключение
        print("🔄 Тестирование подключения к Supabase...")
        
        # Пытаемся выполнить простой запрос
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
    print("="*40)
    
    success = test_supabase_connection()
    
    if success:
        print("\n🎉 Все готово для работы с Supabase!")
        print("💡 Теперь можно запускать: python s3_to_supabase.py")
    else:
        print("\n⚠️ Настройте переменные окружения:")
        print("export SUPABASE_URL=https://your-project.supabase.co")
        print("export SUPABASE_KEY=your_supabase_anon_key")


if __name__ == "__main__":
    main()
