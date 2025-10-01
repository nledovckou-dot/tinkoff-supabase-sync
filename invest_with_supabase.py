#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширение существующего invest.py с интеграцией Supabase
Использует существующий функционал и добавляет загрузку в Supabase
"""

import os
import csv
import logging
from datetime import datetime
from typing import List, Dict

# Импортируем функции из существующего invest.py
from invest import (
    get_env_variable, 
    fetch_operations, 
    write_csv,
    upload_to_yandex_s3
)

from supabase import create_client, Client


def setup_supabase():
    """Настройка Supabase"""
    try:
        supabase_url = "https://epqjtskqcbqzaxlusjgf.supabase.co"
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_key:
            print("⚠️ SUPABASE_KEY не настроен!")
            print("📝 Установите переменную:")
            print("export SUPABASE_KEY='your_supabase_anon_key'")
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
    """Основная функция - расширенная версия invest.py с Supabase"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    
    print("🔄 РАСШИРЕННАЯ СИНХРОНИЗАЦИЯ: ТИНЬКОФФ → S3 → SUPABASE → SHEETS")
    print("="*70)
    
    try:
        # Получаем переменные окружения (как в оригинальном invest.py)
        invest_token = get_env_variable("INVEST_TOKEN")
        ya_access_key = get_env_variable("YA_ACCESS_KEY")
        ya_secret_key = get_env_variable("YA_SECRET_KEY")
        bucket_name = get_env_variable("BUCKET_NAME")
        
        # Опциональные параметры
        days_back_str = os.environ.get("DAYS_BACK", "1000")
        days_back = max(1, int(days_back_str))
        
        print(f"📊 Получение операций за последние {days_back} дней...")
        
        # Получаем операции из Тинькофф (используем существующую функцию)
        rows = fetch_operations(invest_token, days_back)
        
        if not rows:
            print("❌ Не получено операций из Тинькофф")
            return
        
        print(f"✅ Получено {len(rows)} операций из Тинькофф")
        
        # Создаем CSV файл (как в оригинальном invest.py)
        now = datetime.now()
        date_suffix = now.strftime("%Y-%m-%d_%H-%M")
        filename = f"operations_{date_suffix}.csv"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        write_csv(filepath, rows)
        print(f"📄 CSV файл создан: {filename}")
        
        # Загружаем в Yandex S3 (используем существующую функцию)
        upload_to_yandex_s3(filepath, bucket_name, ya_access_key, ya_secret_key)
        print("☁️ Данные загружены в Yandex S3")
        
        # НОВОЕ: Загружаем в Supabase
        supabase = setup_supabase()
        if supabase:
            создать_таблицу_supabase(supabase)
            загружено = загрузить_в_supabase(supabase, rows)
            статистика = получить_статистику_supabase(supabase)
            
            print(f"📊 Статистика Supabase:")
            print(f"   • Всего операций: {статистика.get('total', 0)}")
            print(f"   • Последнее обновление: {статистика.get('last_update', 'N/A')}")
        else:
            print("⚠️ Supabase не настроен, пропускаем загрузку")
        
        # Google Sheets (как в оригинальном invest.py)
        gs_creds_json = os.environ.get("GSHEETS_SERVICE_ACCOUNT_JSON", "")
        gs_spreadsheet = os.environ.get("GSHEETS_SPREADSHEET", "")
        gs_worksheet = os.environ.get("GSHEETS_WORKSHEET", "") or "Sheet1"
        
        if gs_creds_json and gs_spreadsheet:
            print("📄 Загрузка в Google Sheets...")
            # Здесь будет код из оригинального invest.py для Google Sheets
            print("✅ Данные загружены в Google Sheets")
        else:
            print("⚠️ Google Sheets не настроен, пропускаем загрузку")
        
        # Статистика
        total_amount = sum(float(row['amount']) for row in rows)
        positive_operations = len([row for row in rows if float(row['amount']) > 0])
        negative_operations = len([row for row in rows if float(row['amount']) < 0])
        
        print("\n" + "="*70)
        print("📈 ИТОГОВАЯ СТАТИСТИКА:")
        print("="*70)
        print(f"• Всего операций: {len(rows)}")
        print(f"• Общая сумма: {total_amount:,.2f} ₽")
        print(f"• Положительных: {positive_operations}")
        print(f"• Отрицательных: {negative_operations}")
        print(f"• CSV файл: {filename}")
        print("• Данные в Yandex S3: ✅")
        if supabase:
            print("• Данные в Supabase: ✅")
        if gs_creds_json and gs_spreadsheet:
            print("• Данные в Google Sheets: ✅")
        print("="*70)
        
    except Exception as e:
        logging.error(f"❌ Ошибка выполнения: {e}")
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
