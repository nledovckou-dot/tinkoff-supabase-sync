#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест подключения к вашему Supabase
"""

import os
import logging


def test_supabase_connection():
    """Тестирование подключения к Supabase"""
    try:
        from supabase import create_client
        
        # Ваши данные Supabase
        supabase_url = "https://epqjtskqcbqzaxlusjgf.supabase.co"
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_key:
            print("❌ SUPABASE_KEY не настроен!")
            print("📝 Установите переменную:")
            print("export SUPABASE_KEY=your_supabase_anon_key")
            return False
        
        print("🔄 Тестирование подключения к Supabase...")
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


def test_tinkoff_connection():
    """Тестирование подключения к Тинькофф"""
    try:
        invest_token = os.environ.get("INVEST_TOKEN")
        
        if not invest_token:
            print("❌ INVEST_TOKEN не настроен!")
            print("📝 Установите переменную:")
            print("export INVEST_TOKEN=your_tinkoff_token")
            return False
        
        print("🔄 Тестирование подключения к Тинькофф...")
        print(f"Token: {invest_token[:20]}...")
        
        from tinkoff.invest import Client
        
        with Client(invest_token) as client:
            accounts = client.users.get_accounts().accounts
            if accounts:
                print("✅ Подключение к Тинькофф успешно!")
                print(f"📊 Найдено аккаунтов: {len(accounts)}")
                return True
            else:
                print("❌ Нет доступных аккаунтов")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка подключения к Тинькофф: {e}")
        return False


def main():
    """Основная функция"""
    print("🧪 ТЕСТ ПОДКЛЮЧЕНИЙ")
    print("="*50)
    
    # Тест Supabase
    supabase_ok = test_supabase_connection()
    
    print("\n" + "-"*50)
    
    # Тест Тинькофф
    tinkoff_ok = test_tinkoff_connection()
    
    print("\n" + "="*50)
    
    if supabase_ok and tinkoff_ok:
        print("🎉 Все подключения работают!")
        print("💡 Теперь можно запускать: python3 tinkoff_to_supabase.py")
    else:
        print("⚠️ Некоторые подключения не работают")
        print("🔧 Настройте переменные окружения и попробуйте снова")


if __name__ == "__main__":
    main()
