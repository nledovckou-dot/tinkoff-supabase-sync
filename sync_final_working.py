#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Очень простая синхронизация Тинькофф → Supabase
"""

import os
from invest import fetch_operations
from supabase import create_client


def main():
    print("🔄 СИНХРОНИЗАЦИЯ ТИНЬКОФФ → SUPABASE")
    print("="*50)
    
    # Загружаем переменные из файла
    with open('config.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value
    
    # Получаем переменные
    invest_token = os.environ.get("INVEST_TOKEN")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not invest_token:
        print("❌ INVEST_TOKEN не настроен!")
        return
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL или SUPABASE_KEY не настроены!")
        return
    
    print("📊 Получение операций из Тинькофф...")
    
    # Получаем операции
    операции = fetch_operations(invest_token, 1000)
    
    if not операции:
        print("❌ Не получено операций из Тинькофф")
        return
    
    print(f"✅ Получено {len(операций)} операций из Тинькофф")
    
    # Подключаемся к Supabase
    print("🔗 Подключение к Supabase...")
    supabase = create_client(supabase_url, supabase_key)
    
    # Создаем таблицу
    print("📋 Создание таблицы...")
    try:
        sql = """
        CREATE TABLE IF NOT EXISTS tinkoff_operations (
            id SERIAL PRIMARY KEY,
            operation_id VARCHAR(100) UNIQUE NOT NULL,
            date_msk TIMESTAMP NOT NULL,
            action VARCHAR(200) NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            currency VARCHAR(10) NOT NULL,
            status VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ Таблица создана")
    except Exception as e:
        print(f"⚠️ Ошибка создания таблицы: {e}")
    
    # Загружаем данные
    print("💾 Загрузка данных в Supabase...")
    try:
        supabase_data = []
        for операция in операции:
            supabase_data.append({
                'operation_id': операция['operation_id'],
                'date_msk': операция['date_msk'],
                'action': операция['action'],
                'amount': float(операция['amount']),
                'currency': операция['currency'],
                'status': операция['status'],
                'description': операция['description']
            })
        
        result = supabase.table('tinkoff_operations').upsert(
            supabase_data, 
            on_conflict='operation_id'
        ).execute()
        
        print(f"✅ Загружено {len(result.data)} операций в Supabase")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return
    
    # Статистика
    total_amount = sum(float(op['amount']) for op in операции)
    positive_ops = len([op for op in операции if float(op['amount']) > 0])
    negative_ops = len([op for op in операции if float(op['amount']) < 0])
    
    print("\n" + "="*50)
    print("📈 СТАТИСТИКА:")
    print("="*50)
    print(f"• Операций: {len(операций)}")
    print(f"• Общая сумма: {total_amount:,.2f} ₽")
    print(f"• Положительных: {positive_ops}")
    print(f"• Отрицательных: {negative_ops}")
    print("="*50)
    
    print("\n🎉 Синхронизация завершена!")
    print("💡 Проверьте данные в Supabase SQL Editor")


if __name__ == "__main__":
    main()