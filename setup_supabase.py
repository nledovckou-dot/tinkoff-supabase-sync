#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Настройка переменных окружения для Supabase
"""

import os


def setup_supabase_env():
    """Настройка переменных окружения Supabase"""
    print("🔧 НАСТРОЙКА SUPABASE")
    print("="*50)
    
    # Из вашей строки подключения
    supabase_host = "db.epqjtskqcbqzaxlusjgf.supabase.co"
    supabase_port = "5432"
    supabase_db = "postgres"
    supabase_user = "postgres"
    
    print(f"📊 Данные из строки подключения:")
    print(f"   Host: {supabase_host}")
    print(f"   Port: {supabase_port}")
    print(f"   Database: {supabase_db}")
    print(f"   Username: {supabase_user}")
    print(f"   Password: [YOUR-PASSWORD] - нужно заменить на реальный")
    
    print("\n" + "="*50)
    print("🔗 Для работы с Supabase нужны:")
    print("1. SUPABASE_URL (для REST API)")
    print("2. SUPABASE_KEY (для REST API)")
    print("3. INVEST_TOKEN (для Тинькофф)")
    
    print("\n📝 Установите переменные окружения:")
    print("export SUPABASE_URL=https://epqjtskqcbqzaxlusjgf.supabase.co")
    print("export SUPABASE_KEY=your_supabase_anon_key")
    print("export INVEST_TOKEN=your_tinkoff_token")
    
    print("\n🔍 Как найти SUPABASE_URL и SUPABASE_KEY:")
    print("1. Зайдите на supabase.com")
    print("2. Откройте ваш проект")
    print("3. Перейдите в Settings → API")
    print("4. Скопируйте Project URL и anon public ключ")
    
    print("\n🎯 После настройки запустите:")
    print("python3 tinkoff_to_supabase.py")


if __name__ == "__main__":
    setup_supabase_env()
