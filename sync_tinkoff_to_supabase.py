#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск синхронизации Тинькофф → Supabase (без S3)
Использует существующий invest.py и добавляет Supabase
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict

# Импортируем функции из существующего invest.py
from invest import (
    get_env_variable, 
    fetch_operations
)

from supabase import create_client, Client


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


def setup_supabase():
    """Настройка Supabase"""
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL или SUPABASE_KEY не настроены!")
            return None
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase подключен")
        return supabase
        
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        return None


def создать_таблицу_supabase(supabase: Client):
    """Создание таблицы в Supabase"""
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
        print("✅ Таблица tinkoff_operations создана в Supabase")
        
    except Exception as e:
        print(f"⚠️ Ошибка создания таблицы: {e}")


def загрузить_в_supabase(supabase: Client, операции: List[Dict]) -> int:
    """Загрузка операций в Supabase"""
    try:
        if not операции:
            print("⚠️ Нет операций для загрузки")
            return 0
        
        # Преобразуем данные для Supabase
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
        
        # Загружаем данные в Supabase (upsert - обновляем существующие)
        result = supabase.table('tinkoff_operations').upsert(
            supabase_data, 
            on_conflict='operation_id'
        ).execute()
        
        загружено = len(result.data)
        print(f"✅ Загружено {загружено} операций в Supabase")
        
        return загружено
        
    except Exception as e:
        print(f"❌ Ошибка загрузки в Supabase: {e}")
        return 0


def получить_статистику_supabase(supabase: Client) -> Dict:
    """Получение статистики из Supabase"""
    try:
        result = supabase.table('tinkoff_operations').select('*', count='exact').execute()
        total = result.count if result.count else 0
        
        last_op = supabase.table('tinkoff_operations').select('date_msk').order('date_msk', desc=True).limit(1).execute()
        last_update = last_op.data[0]['date_msk'] if last_op.data else ''
        
        return {
            'total': total,
            'last_update': last_update
        }
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        return {'total': 0, 'last_update': ''}


def main():
    """Основная функция"""
    print("🔄 СИНХРОНИЗАЦИЯ ТИНЬКОФФ → SUPABASE")
    print("="*60)
    
    # Загружаем переменные из файла
    if not load_env_from_file():
        return
    
    try:
        # Получаем переменные окружения
        invest_token = os.environ.get("INVEST_TOKEN")
        days_back_str = os.environ.get("DAYS_BACK", "1000")
        days_back = max(1, int(days_back_str))
        
        if not invest_token:
            print("❌ INVEST_TOKEN не настроен!")
            print("📝 Установите токен Тинькофф в config.env")
            return
        
        print(f"📊 Получение операций за последние {days_back} дней...")
        
        # Получаем операции из Тинькофф
        операции = fetch_operations(invest_token, days_back)
        
        if not операции:
            print("❌ Не получено операций из Тинькофф")
            return
        
        print(f"✅ Получено {len(операций)} операций из Тинькофф")
        
        # Настраиваем Supabase
        supabase = setup_supabase()
        if not supabase:
            return
        
        # Создаем таблицу
        создать_таблицу_supabase(supabase)
        
        # Загружаем данные
        загружено = загрузить_в_supabase(supabase, операции)
        
        # Получаем статистику
        статистика = получить_статистику_supabase(supabase)
        
        # Итоговая статистика
        total_amount = sum(float(op['amount']) for op in операции)
        positive_ops = len([op for op in операции if float(op['amount']) > 0])
        negative_ops = len([op for op in операции if float(op['amount']) < 0])
        
        print("\n" + "="*60)
        print("📈 ИТОГОВАЯ СТАТИСТИКА:")
        print("="*60)
        print(f"• Операций получено: {len(операций)}")
        print(f"• Загружено в Supabase: {загружено}")
        print(f"• Всего в Supabase: {статистика.get('total', 0)}")
        print(f"• Общая сумма: {total_amount:,.2f} ₽")
        print(f"• Положительных: {positive_ops}")
        print(f"• Отрицательных: {negative_ops}")
        print(f"• Последнее обновление: {статистика.get('last_update', 'N/A')}")
        print("="*60)
        
        print("\n🎉 Синхронизация завершена успешно!")
        print("💡 Проверьте данные в Supabase SQL Editor")
        
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")


if __name__ == "__main__":
    main()
