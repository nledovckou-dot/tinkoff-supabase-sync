#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка существующих переменных окружения
"""

import os


def check_existing_env():
    """Проверка существующих переменных окружения"""
    print("🔍 ПРОВЕРКА СУЩЕСТВУЮЩИХ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("="*60)
    
    # Переменные из invest.py
    env_vars = {
        'INVEST_TOKEN': 'Токен Тинькофф (обязательно)',
        'YA_ACCESS_KEY': 'Ключ доступа Yandex S3 (обязательно)',
        'YA_SECRET_KEY': 'Секретный ключ Yandex S3 (обязательно)',
        'BUCKET_NAME': 'Имя bucket Yandex S3 (обязательно)',
        'DAYS_BACK': 'Количество дней назад (опционально)',
        'GSHEETS_SERVICE_ACCOUNT_JSON': 'JSON ключ Google Sheets (опционально)',
        'GSHEETS_SPREADSHEET': 'ID таблицы Google Sheets (опционально)',
        'GSHEETS_WORKSHEET': 'Название листа Google Sheets (опционально)',
        'SUPABASE_KEY': 'Ключ Supabase (для новой интеграции)'
    }
    
    print("📋 Статус переменных:")
    for var, описание in env_vars.items():
        value = os.environ.get(var)
        if value:
            if var == 'INVEST_TOKEN':
                print(f"   ✅ {var}: {'*' * min(len(value), 20)}... - {описание}")
            elif var == 'SUPABASE_KEY':
                print(f"   ✅ {var}: {'*' * min(len(value), 20)}... - {описание}")
            else:
                print(f"   ✅ {var}: {'*' * min(len(value), 10)}... - {описание}")
        else:
            print(f"   ❌ {var}: НЕ НАСТРОЕНА - {описание}")
    
    print("\n" + "="*60)
    
    # Проверяем минимальные требования
    обязательные = ['INVEST_TOKEN', 'YA_ACCESS_KEY', 'YA_SECRET_KEY', 'BUCKET_NAME']
    настроено = all(os.environ.get(var) for var in обязательные)
    
    if настроено:
        print("🎉 Минимальные требования выполнены!")
        print("💡 Можно запускать:")
        print("   python3 invest.py                    # Оригинальный скрипт")
        print("   python3 invest_with_supabase.py      # С интеграцией Supabase")
    else:
        print("⚠️ Не все обязательные переменные настроены")
        print("🔧 Настройте переменные и попробуйте снова")
    
    print("\n" + "="*60)
    print("🔍 КАК НАЙТИ ПЕРЕМЕННЫЕ:")
    print("="*60)
    print("1. Проверьте файл .env в текущей директории")
    print("2. Проверьте файл .bashrc или .zshrc")
    print("3. Проверьте переменные окружения системы")
    print("4. Запустите: env | grep -E '(INVEST|YA_|BUCKET|SUPABASE)'")


if __name__ == "__main__":
    check_existing_env()