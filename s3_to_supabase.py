#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для передачи данных из Yandex S3 в Supabase
Получает CSV файлы из S3 и загружает их в Supabase
"""

import os
import csv
import json
import logging
import tempfile
from datetime import datetime
from typing import List, Dict, Optional

import boto3
from botocore.config import Config
from supabase import create_client, Client


def get_env_variable(name: str) -> str:
    """Получение переменной окружения"""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def get_optional_env_variable(name: str, default: str = "") -> str:
    """Получение опциональной переменной окружения"""
    return os.environ.get(name, default)


class S3ToSupabase:
    """Класс для передачи данных из S3 в Supabase"""
    
    def __init__(self):
        """Инициализация подключений"""
        # Yandex S3
        self.ya_access_key = get_env_variable("YA_ACCESS_KEY")
        self.ya_secret_key = get_env_variable("YA_SECRET_KEY")
        self.bucket_name = get_env_variable("BUCKET_NAME")
        
        # Supabase
        self.supabase_url = get_env_variable("SUPABASE_URL")
        self.supabase_key = get_env_variable("SUPABASE_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Настройка S3 клиента
        self.s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=self.ya_access_key,
            aws_secret_access_key=self.ya_secret_key,
            endpoint_url="https://storage.yandexcloud.net",
            region_name="ru-central1",
            config=Config(signature_version="s3v4"),
        )
        
        logging.info("✅ Подключения к S3 и Supabase настроены")
    
    def создать_таблицу_supabase(self) -> None:
        """Создание таблицы в Supabase для операций Тинькофф"""
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
    
    def получить_список_файлов_s3(self) -> List[str]:
        """Получение списка CSV файлов из S3"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            csv_files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.csv') and 'operations' in key:
                        csv_files.append(key)
            
            logging.info(f"📁 Найдено {len(csv_files)} CSV файлов в S3")
            return csv_files
            
        except Exception as e:
            logging.error(f"❌ Ошибка получения списка файлов из S3: {e}")
            return []
    
    def скачать_файл_из_s3(self, key: str) -> Optional[str]:
        """Скачивание файла из S3 во временную директорию"""
        try:
            temp_file = os.path.join(tempfile.gettempdir(), f"temp_{key}")
            
            self.s3_client.download_file(self.bucket_name, key, temp_file)
            logging.info(f"📥 Файл {key} скачан во временную директорию")
            
            return temp_file
            
        except Exception as e:
            logging.error(f"❌ Ошибка скачивания файла {key}: {e}")
            return None
    
    def загрузить_csv_в_supabase(self, file_path: str) -> int:
        """Загрузка данных из CSV файла в Supabase"""
        try:
            операции = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Преобразуем данные для Supabase
                    операция = {
                        'operation_id': row['operation_id'],
                        'date_msk': row['date_msk'],
                        'action': row['action'],
                        'amount': float(row['amount']),
                        'currency': row['currency'],
                        'status': row['status'],
                        'description': row['description']
                    }
                    операции.append(операция)
            
            if not операции:
                logging.warning("⚠️ Нет данных для загрузки")
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
            logging.error(f"❌ Ошибка загрузки CSV в Supabase: {e}")
            return 0
    
    def получить_последний_файл(self) -> Optional[str]:
        """Получение последнего файла из S3"""
        try:
            # Пытаемся получить latest.json
            try:
                latest_info = self.s3_client.get_object(Bucket=self.bucket_name, Key="latest.json")
                latest_data = json.loads(latest_info['Body'].read().decode('utf-8'))
                latest_file = latest_data.get('key')
                
                if latest_file:
                    logging.info(f"📄 Последний файл из latest.json: {latest_file}")
                    return latest_file
                    
            except Exception:
                logging.info("📄 latest.json не найден, ищем последний CSV файл")
            
            # Если latest.json нет, ищем последний CSV файл
            csv_files = self.получить_список_файлов_s3()
            if csv_files:
                # Сортируем по дате создания (последний файл)
                csv_files.sort(reverse=True)
                latest_file = csv_files[0]
                logging.info(f"📄 Последний CSV файл: {latest_file}")
                return latest_file
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Ошибка получения последнего файла: {e}")
            return None
    
    def синхронизировать_данные(self) -> Dict:
        """Синхронизация данных из S3 в Supabase"""
        try:
            logging.info("🔄 Начинаем синхронизацию данных S3 → Supabase")
            
            # Создаем таблицу в Supabase
            self.создать_таблицу_supabase()
            
            # Получаем последний файл
            latest_file = self.получить_последний_файл()
            
            if not latest_file:
                logging.warning("⚠️ Не найден файл для синхронизации")
                return {'status': 'error', 'message': 'Файл не найден'}
            
            # Скачиваем файл
            temp_file = self.скачать_файл_из_s3(latest_file)
            
            if not temp_file:
                return {'status': 'error', 'message': 'Ошибка скачивания файла'}
            
            # Загружаем в Supabase
            загружено = self.загрузить_csv_в_supabase(temp_file)
            
            # Удаляем временный файл
            try:
                os.remove(temp_file)
            except Exception:
                pass
            
            # Получаем статистику из Supabase
            stats = self.получить_статистику_supabase()
            
            результат = {
                'status': 'success',
                'file': latest_file,
                'loaded_operations': загружено,
                'total_operations': stats.get('total', 0),
                'last_update': stats.get('last_update', ''),
                'sync_time': datetime.now().isoformat()
            }
            
            logging.info("✅ Синхронизация завершена успешно")
            return результат
            
        except Exception as e:
            logging.error(f"❌ Ошибка синхронизации: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def получить_статистику_supabase(self) -> Dict:
        """Получение статистики из Supabase"""
        try:
            # Получаем общее количество операций
            result = self.supabase.table('tinkoff_operations').select('*', count='exact').execute()
            total = result.count if result.count else 0
            
            # Получаем последнюю операцию
            last_op = self.supabase.table('tinkoff_operations').select('date_msk').order('date_msk', desc=True).limit(1).execute()
            last_update = last_op.data[0]['date_msk'] if last_op.data else ''
            
            return {
                'total': total,
                'last_update': last_update
            }
            
        except Exception as e:
            logging.error(f"❌ Ошибка получения статистики: {e}")
            return {'total': 0, 'last_update': ''}
    
    def создать_отчет(self, результат: Dict) -> str:
        """Создание отчета о синхронизации"""
        отчет = f"""
{'='*60}
ОТЧЕТ СИНХРОНИЗАЦИИ S3 → SUPABASE
{'='*60}
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
Статус: {результат.get('status', 'unknown')}

📊 РЕЗУЛЬТАТЫ:
• Файл: {результат.get('file', 'N/A')}
• Загружено операций: {результат.get('loaded_operations', 0)}
• Всего операций в Supabase: {результат.get('total_operations', 0)}
• Последнее обновление: {результат.get('last_update', 'N/A')}
• Время синхронизации: {результат.get('sync_time', 'N/A')}

{'='*60}
"""
        
        if результат.get('status') == 'success':
            отчет += "✅ Синхронизация выполнена успешно!\n"
        else:
            отчет += f"❌ Ошибка: {результат.get('message', 'Unknown error')}\n"
        
        отчет += "="*60
        
        return отчет


def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler('s3_to_supabase.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        print("🔄 СИНХРОНИЗАЦИЯ S3 → SUPABASE")
        print("="*50)
        
        # Создаем экземпляр синхронизатора
        синхронизатор = S3ToSupabase()
        
        # Выполняем синхронизацию
        результат = синхронизатор.синхронизировать_данные()
        
        # Создаем отчет
        отчет = синхронизатор.создать_отчет(результат)
        
        # Сохраняем отчет
        with open('отчет_синхронизации.txt', 'w', encoding='utf-8') as f:
            f.write(отчет)
        
        # Выводим результат
        print(отчет)
        
        if результат.get('status') == 'success':
            print("\n🎉 Синхронизация завершена успешно!")
            print("📄 Отчет сохранен в файл 'отчет_синхронизации.txt'")
        else:
            print(f"\n❌ Ошибка синхронизации: {результат.get('message')}")
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
