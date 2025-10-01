#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая загрузка данных из S3 в Supabase (без создания таблицы)
"""

import os
import csv
from supabase import create_client


def load_env_from_file(filename='config.env'):
    """Загрузка переменных окружения из файла"""
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value


def upload_to_supabase(csv_file):
    """Загрузка данных в Supabase"""
    try:
        # Подключение к Supabase
        supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
        
        print("✅ Подключение к Supabase установлено")
        
        # Чтение CSV и загрузка в Supabase
        supabase_data = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                supabase_data.append({
                    'operation_id': row['operation_id'],
                    'date_msk': row['date_msk'],
                    'action': row['action'],
                    'amount': float(row['amount']),
                    'currency': row['currency'],
                    'status': row['status'],
                    'description': row['description']
                })
        
        print(f"📊 Прочитано {len(supabase_data)} операций из CSV")
        
        # Загрузка данных
        result = supabase.table('tinkoff_operations').upsert(
            supabase_data, 
            on_conflict='operation_id'
        ).execute()
        
        print(f"✅ Загружено {len(result.data)} операций в Supabase")
        
        return len(result.data)
        
    except Exception as e:
        print(f"❌ Ошибка загрузки в Supabase: {e}")
        return 0


def main():
    """Основная функция"""
    print("🔄 ЗАГРУЗКА S3 → SUPABASE")
    print("="*50)
    
    # Загружаем переменные
    load_env_from_file()
    
    # Загружаем в Supabase
    uploaded = upload_to_supabase("operations_latest.csv")
    
    if uploaded > 0:
        print(f"\n🎉 Успешно загружено {uploaded} операций в Supabase!")
        print("💡 Проверьте данные в Supabase SQL Editor")
    else:
        print("\n❌ Ошибка загрузки в Supabase")


if __name__ == "__main__":
    main()