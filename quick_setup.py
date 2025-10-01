#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая настройка проекта
"""

import os
import shutil


def quick_setup():
    """Быстрая настройка проекта"""
    print("🚀 БЫСТРАЯ НАСТРОЙКА ПРОЕКТА")
    print("="*50)
    
    # Проверяем существующие файлы
    files_to_check = [
        'invest.py',
        'config.env', 
        'config_template.env',
        'run_invest.py'
    ]
    
    print("📁 Проверяем файлы проекта:")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - отсутствует")
    
    print("\n" + "="*50)
    
    # Копируем шаблон в config.env если нужно
    if os.path.exists('config_template.env') and not os.path.exists('config.env'):
        shutil.copy('config_template.env', 'config.env')
        print("✅ Создан config.env из шаблона")
    elif os.path.exists('config.env'):
        print("✅ config.env уже существует")
    
    print("\n" + "="*50)
    print("🔧 СЛЕДУЮЩИЕ ШАГИ:")
    print("="*50)
    
    print("1. Откройте файл config.env в текстовом редакторе")
    print("2. Замените шаблоны на реальные значения:")
    print("   • INVEST_TOKEN - токен Тинькофф")
    print("   • SUPABASE_KEY - ключ Supabase") 
    print("   • YA_ACCESS_KEY - ключ Yandex S3")
    print("   • YA_SECRET_KEY - секретный ключ Yandex S3")
    print("   • BUCKET_NAME - имя bucket")
    
    print("\n3. Сохраните файл")
    print("4. Запустите: python3 run_invest.py")
    
    print("\n" + "="*50)
    print("💡 СОВЕТЫ:")
    print("="*50)
    print("• Начните с минимального набора: INVEST_TOKEN + SUPABASE_KEY")
    print("• Yandex S3 можно настроить позже")
    print("• Google Sheets опционально")
    
    print("\n🎯 МИНИМАЛЬНАЯ НАСТРОЙКА:")
    print("="*50)
    print("INVEST_TOKEN=ваш_токен_тинькофф")
    print("SUPABASE_URL=https://epqjtskqcbqzaxlusjgf.supabase.co")
    print("SUPABASE_KEY=ваш_ключ_supabase")


if __name__ == "__main__":
    quick_setup()