#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ежедневная синхронизация: Тинькофф → S3 → Supabase (исправленная версия)
"""

import os
import csv
import logging
import tempfile
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


def load_env_from_file(filename='config.env'):
    """Загрузка переменных окружения из файла"""
    if not os.path.exists(filename):
        logging.error(f"Файл {filename} не найден")
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
            logging.error("SUPABASE_URL или SUPABASE_KEY не настроены")
            return None
        
        supabase = create_client(supabase_url, supabase_key)
        logging.info("Supabase подключен")
        return supabase
        
    except Exception as e:
        logging.error(f"Ошибка подключения к Supabase: {e}")
        return None


def upload_to_supabase(supabase: Client, операции: List[Dict]) -> int:
    """Загрузка операций в Supabase"""
    try:
        if not операции:
            logging.warning("Нет операций для загрузки")
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
        logging.info(f"Загружено {загружено} операций в Supabase")
        
        return загружено
        
    except Exception as e:
        logging.error(f"Ошибка загрузки в Supabase: {e}")
        return 0


def get_supabase_stats(supabase: Client) -> Dict:
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
        logging.error(f"Ошибка получения статистики: {e}")
        return {'total': 0, 'last_update': ''}


def daily_sync():
    """Ежедневная синхронизация"""
    # Настройка логирования
    log_file = f"daily_sync_{datetime.now().strftime('%Y-%m-%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info("🔄 НАЧАЛО ЕЖЕДНЕВНОЙ СИНХРОНИЗАЦИИ")
    logging.info("="*60)
    
    try:
        # Загружаем переменные окружения
        if not load_env_from_file():
            return False
        
        # Получаем переменные
        invest_token = os.environ.get("INVEST_TOKEN")
        ya_access_key = os.environ.get("YA_ACCESS_KEY")
        ya_secret_key = os.environ.get("YA_SECRET_KEY")
        bucket_name = os.environ.get("BUCKET_NAME")
        days_back_str = os.environ.get("DAYS_BACK", "1000")
        days_back = max(1, int(days_back_str))
        
        if not all([invest_token, ya_access_key, ya_secret_key, bucket_name]):
            logging.error("Не все обязательные переменные настроены")
            return False
        
        logging.info(f"Получение операций за последние {days_back} дней...")
        
        # Получаем операции из Тинькофф
        операции = fetch_operations(invest_token, days_back)
        
        if not операции:
            logging.error("Не получено операций из Тинькофф")
            return False
        
        logging.info(f"Получено {len(операций)} операций из Тинькофф")
        
        # Создаем CSV файл
        now = datetime.now()
        date_suffix = now.strftime("%Y-%m-%d_%H-%M")
        filename = f"operations_{date_suffix}.csv"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        write_csv(filepath, операции)
        logging.info(f"CSV файл создан: {filename}")
        
        # Загружаем в Yandex S3
        upload_to_yandex_s3(filepath, bucket_name, ya_access_key, ya_secret_key)
        logging.info("Данные загружены в Yandex S3")
        
        # Загружаем в Supabase
        supabase = setup_supabase()
        if supabase:
            загружено = upload_to_supabase(supabase, операции)
            статистика = get_supabase_stats(supabase)
            
            logging.info(f"Статистика Supabase:")
            logging.info(f"  • Всего операций: {статистика.get('total', 0)}")
            logging.info(f"  • Последнее обновление: {статистика.get('last_update', 'N/A')}")
        else:
            logging.warning("Supabase не настроен, пропускаем загрузку")
            загружено = 0
        
        # Итоговая статистика
        total_amount = sum(float(op['amount']) for op in операции)
        positive_ops = len([op for op in операции if float(op['amount']) > 0])
        negative_ops = len([op for op in операции if float(op['amount']) < 0])
        
        logging.info("="*60)
        logging.info("📈 ИТОГОВАЯ СТАТИСТИКА:")
        logging.info("="*60)
        logging.info(f"• Операций получено: {len(операций)}")
        logging.info(f"• Загружено в Supabase: {загружено}")
        logging.info(f"• Общая сумма: {total_amount:,.2f} ₽")
        logging.info(f"• Положительных: {positive_ops}")
        logging.info(f"• Отрицательных: {negative_ops}")
        logging.info(f"• CSV файл: {filename}")
        logging.info("• Данные в Yandex S3: ✅")
        if supabase:
            logging.info("• Данные в Supabase: ✅")
        logging.info("="*60)
        
        logging.info("✅ ЕЖЕДНЕВНАЯ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        return True
        
    except Exception as e:
        logging.error(f"❌ Ошибка ежедневной синхронизации: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция"""
    success = daily_sync()
    
    if success:
        print("🎉 Ежедневная синхронизация завершена успешно!")
        print("📊 Проверьте данные в Supabase SQL Editor")
    else:
        print("❌ Ошибка ежедневной синхронизации")
        print("📋 Проверьте лог файл для деталей")


if __name__ == "__main__":
    main()