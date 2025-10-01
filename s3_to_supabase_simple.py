#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка данных из Yandex S3 в Supabase
"""

import os
import csv
import tempfile
from supabase import create_client
import boto3
from botocore.config import Config


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


def download_from_s3():
    """Скачивание файла из S3"""
    try:
        # Настройка S3 клиента
        s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=os.environ.get("YA_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("YA_SECRET_KEY"),
            endpoint_url="https://storage.yandexcloud.net",
            region_name="ru-central1",
            config=Config(signature_version="s3v4"),
        )
        
        bucket_name = os.environ.get("BUCKET_NAME")
        
        # Скачиваем последний файл
        s3_client.download_file(bucket_name, "operations_latest.csv", "operations_latest.csv")
        print("✅ Файл скачан из S3")
        
        return "operations_latest.csv"
        
    except Exception as e:
        print(f"❌ Ошибка скачивания из S3: {e}")
        return None


def upload_to_supabase(csv_file):
    """Загрузка данных в Supabase"""
    try:
        # Подключение к Supabase
        supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
        
        # Создание таблицы
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
        print("✅ Таблица создана в Supabase")
        
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
    
    # Скачиваем из S3
    csv_file = download_from_s3()
    if not csv_file:
        return
    
    # Загружаем в Supabase
    uploaded = upload_to_supabase(csv_file)
    
    if uploaded > 0:
        print(f"\n🎉 Успешно загружено {uploaded} операций в Supabase!")
        print("💡 Проверьте данные в Supabase SQL Editor")
    else:
        print("\n❌ Ошибка загрузки в Supabase")


if __name__ == "__main__":
    main()