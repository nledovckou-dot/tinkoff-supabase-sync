#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой редактор config.env
"""

import os


def edit_config():
    """Редактирование config.env"""
    print("✏️ РЕДАКТИРОВАНИЕ CONFIG.ENV")
    print("="*50)
    
    if not os.path.exists('config.env'):
        print("❌ Файл config.env не найден")
        return
    
    print("📝 Открываем config.env для редактирования...")
    print("\n🔧 ЗАМЕНИТЕ ШАБЛОНЫ НА РЕАЛЬНЫЕ ЗНАЧЕНИЯ:")
    print("="*50)
    
    # Показываем текущее содержимое
    with open('config.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(content)
    
    print("\n" + "="*50)
    print("💡 ПРИМЕРЫ ЗАМЕНЫ:")
    print("="*50)
    print("❌ INVEST_TOKEN=your_tinkoff_invest_token_here")
    print("✅ INVEST_TOKEN=t.1234567890abcdef...")
    print()
    print("❌ SUPABASE_KEY=your_supabase_anon_key_here") 
    print("✅ SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    print()
    print("❌ YA_ACCESS_KEY=your_yandex_access_key_here")
    print("✅ YA_ACCESS_KEY=YCAJE...")
    
    print("\n" + "="*50)
    print("🚀 ПОСЛЕ РЕДАКТИРОВАНИЯ:")
    print("="*50)
    print("1. Сохраните файл")
    print("2. Запустите: python3 run_invest.py")
    print("3. Проверьте результаты в Supabase")


def show_minimal_config():
    """Показать минимальную конфигурацию"""
    print("\n🎯 МИНИМАЛЬНАЯ КОНФИГУРАЦИЯ (для начала):")
    print("="*50)
    
    minimal_config = """# Минимальная конфигурация для начала
INVEST_TOKEN=ваш_токен_тинькофф_здесь
SUPABASE_URL=https://epqjtskqcbqzaxlusjgf.supabase.co
SUPABASE_KEY=ваш_ключ_supabase_здесь
DAYS_BACK=1000"""
    
    print(minimal_config)
    
    print("\n💡 Начните с этих 3 переменных:")
    print("• INVEST_TOKEN - получите в Тинькофф")
    print("• SUPABASE_KEY - получите в Supabase")
    print("• Остальные можно настроить позже")


if __name__ == "__main__":
    edit_config()
    show_minimal_config()
