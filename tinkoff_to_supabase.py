#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенная версия: Тинькофф → Supabase (без S3)
Прямая передача данных из Тинькофф в Supabase
"""

import os
import logging
from datetime import datetime
from typing import List, Dict

from tinkoff.invest import Client
from supabase import create_client, Client


def get_env_variable(name: str) -> str:
    """Получение переменной окружения"""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


class TinkoffToSupabase:
    """Класс для прямой передачи данных Тинькофф → Supabase"""
    
    def __init__(self):
        """Инициализация подключений"""
        # Тинькофф
        self.invest_token = get_env_variable("INVEST_TOKEN")
        
        # Supabase
        self.supabase_url = get_env_variable("SUPABASE_URL")
        self.supabase_key = get_env_variable("SUPABASE_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        logging.info("✅ Подключения к Тинькофф и Supabase настроены")
    
    def создать_таблицу_supabase(self) -> None:
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
            
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            logging.info("✅ Таблица tinkoff_operations создана в Supabase")
            
        except Exception as e:
            logging.warning(f"⚠️ Ошибка создания таблицы: {e}")
    
    def получить_операции_тинькофф(self, days_back: int = 1000) -> List[Dict]:
        """Получение операций из Тинькофф"""
        try:
            from zoneinfo import ZoneInfo
            from decimal import Decimal, ROUND_HALF_UP
            
            # Импортируем функции из invest.py
            from invest import build_date_range, _money_to_decimal_str, _rus_operation_type, _rus_operation_state
            
            start_date, end_date = build_date_range(days_back)
            logging.info("Получение операций из Тинькофф с %s по %s", start_date, end_date)

            with Client(self.invest_token) as client:
                accounts = client.users.get_accounts().accounts
                if not accounts:
                    raise RuntimeError("No Tinkoff Invest accounts available for the token")

                account_id = accounts[0].id
                operations = client.operations.get_operations(
                    account_id=account_id,
                    from_=start_date,
                    to=end_date,
                )

                операции = []
                msk = ZoneInfo("Europe/Moscow")
                
                for op in operations.operations:
                    # Генерация ID операции
                    op_id = (
                        getattr(op, "id", None)
                        or getattr(op, "operation_id", None)
                        or getattr(op, "trade_id", None)
                    )
                    if not op_id:
                        fingerprint = (
                            f"{getattr(op, 'date', '')}|{getattr(op, 'type', '')}|"
                            f"{getattr(op, 'currency', '')}|{getattr(op, 'payment', '')}|"
                            f"{getattr(op, 'status', '')}|{getattr(op, 'description', '')}"
                        )
                        op_id = str(abs(hash(fingerprint)))

                    # Обработка даты
                    raw_dt = getattr(op, "date", None)
                    if isinstance(raw_dt, datetime):
                        try:
                            local_dt = raw_dt.astimezone(msk)
                        except Exception:
                            local_dt = raw_dt
                        date_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date_str = str(raw_dt)

                    amount_str = _money_to_decimal_str(getattr(op, "payment", None))
                    action_ru = _rus_operation_type(getattr(op, "type", ""))
                    status_ru = _rus_operation_state(getattr(op, "status", ""))

                    операции.append({
                        "operation_id": str(op_id),
                        "date_msk": date_str,
                        "action": action_ru,
                        "amount": float(amount_str),
                        "currency": str(getattr(op, "currency", "")),
                        "status": status_ru,
                        "description": str(getattr(op, "description", ""))
                    })

                logging.info("Получено %d операций из Тинькофф", len(операции))
                return операции
                
        except Exception as e:
            logging.error(f"Ошибка получения операций из Тинькофф: {e}")
            return []
    
    def загрузить_в_supabase(self, операции: List[Dict]) -> int:
        """Загрузка операций в Supabase"""
        try:
            if not операции:
                logging.warning("Нет операций для загрузки")
                return 0
            
            # Загружаем данные в Supabase (upsert - обновляем существующие)
            result = self.supabase.table('tinkoff_operations').upsert(
                операции, 
                on_conflict='operation_id'
            ).execute()
            
            загружено = len(result.data)
            logging.info(f"✅ Загружено {загружено} операций в Supabase")
            
            return загружено
            
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки в Supabase: {e}")
            return 0
    
    def получить_статистику(self) -> Dict:
        """Получение статистики из Supabase"""
        try:
            result = self.supabase.table('tinkoff_operations').select('*', count='exact').execute()
            total = result.count if result.count else 0
            
            last_op = self.supabase.table('tinkoff_operations').select('date_msk').order('date_msk', desc=True).limit(1).execute()
            last_update = last_op.data[0]['date_msk'] if last_op.data else ''
            
            return {
                'total': total,
                'last_update': last_update
            }
            
        except Exception as e:
            logging.error(f"❌ Ошибка получения статистики: {e}")
            return {'total': 0, 'last_update': ''}
    
    def синхронизировать(self) -> Dict:
        """Основная функция синхронизации"""
        try:
            logging.info("🔄 Начинаем синхронизацию Тинькофф → Supabase")
            
            # Создаем таблицу
            self.создать_таблицу_supabase()
            
            # Получаем операции из Тинькофф
            операции = self.получить_операции_тинькофф()
            
            if not операции:
                return {'status': 'error', 'message': 'Не получено операций из Тинькофф'}
            
            # Загружаем в Supabase
            загружено = self.загрузить_в_supabase(операции)
            
            # Получаем статистику
            stats = self.получить_статистику()
            
            результат = {
                'status': 'success',
                'total_operations': len(операции),
                'loaded_operations': загружено,
                'total_in_supabase': stats.get('total', 0),
                'last_update': stats.get('last_update', ''),
                'sync_time': datetime.now().isoformat()
            }
            
            logging.info("✅ Синхронизация завершена успешно")
            return результат
            
        except Exception as e:
            logging.error(f"❌ Ошибка синхронизации: {e}")
            return {'status': 'error', 'message': str(e)}


def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler('tinkoff_to_supabase.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        print("🔄 СИНХРОНИЗАЦИЯ ТИНЬКОФФ → SUPABASE")
        print("="*50)
        
        # Создаем экземпляр синхронизатора
        синхронизатор = TinkoffToSupabase()
        
        # Выполняем синхронизацию
        результат = синхронизатор.синхронизировать()
        
        # Выводим результат
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"• Статус: {результат.get('status')}")
        print(f"• Операций получено: {результат.get('total_operations', 0)}")
        print(f"• Загружено в Supabase: {результат.get('loaded_operations', 0)}")
        print(f"• Всего в Supabase: {результат.get('total_in_supabase', 0)}")
        print(f"• Последнее обновление: {результат.get('last_update', 'N/A')}")
        
        if результат.get('status') == 'success':
            print("\n🎉 Синхронизация завершена успешно!")
            print("💡 Проверьте данные в Supabase SQL Editor")
        else:
            print(f"\n❌ Ошибка: {результат.get('message')}")
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
