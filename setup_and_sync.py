#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для настройки переменных окружения и запуска синхронизации
"""

import os
import subprocess
import sys


def setup_environment():
    """Настройка переменных окружения"""
    print("🔧 НАСТРОЙКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("="*50)
    
    # Проверяем существующие переменные
    env_vars = {
        'SUPABASE_URL': os.environ.get('SUPABASE_URL'),
        'SUPABASE_KEY': os.environ.get('SUPABASE_KEY'),
        'YA_ACCESS_KEY': os.environ.get('YA_ACCESS_KEY'),
        'YA_SECRET_KEY': os.environ.get('YA_SECRET_KEY'),
        'BUCKET_NAME': os.environ.get('BUCKET_NAME')
    }
    
    print("📋 Текущие переменные окружения:")
    for var, value in env_vars.items():
        if value:
            print(f"   ✅ {var}: {'*' * min(len(value), 20)}...")
        else:
            print(f"   ❌ {var}: НЕ НАСТРОЕНА")
    
    print("\n" + "="*50)
    
    # Если переменные не настроены, предлагаем их ввести
    if not env_vars['SUPABASE_URL'] or not env_vars['SUPABASE_KEY']:
        print("⚠️ Переменные Supabase не настроены!")
        print("\n🔗 Как получить ключи Supabase:")
        print("1. Зайдите на supabase.com")
        print("2. Откройте ваш проект")
        print("3. Перейдите в Settings → API")
        print("4. Скопируйте Project URL и anon public ключ")
        print("\n📝 Введите ваши ключи:")
        
        supabase_url = input("SUPABASE_URL (https://your-project.supabase.co): ").strip()
        supabase_key = input("SUPABASE_KEY (длинная строка): ").strip()
        
        if supabase_url and supabase_key:
            os.environ['SUPABASE_URL'] = supabase_url
            os.environ['SUPABASE_KEY'] = supabase_key
            print("✅ Переменные Supabase настроены!")
        else:
            print("❌ Переменные Supabase не введены")
            return False
    
    # Проверяем переменные Yandex S3
    if not env_vars['YA_ACCESS_KEY'] or not env_vars['YA_SECRET_KEY'] or not env_vars['BUCKET_NAME']:
        print("\n⚠️ Переменные Yandex S3 не настроены!")
        print("Без них синхронизация не будет работать.")
        print("\n🔗 Как получить ключи Yandex S3:")
        print("1. Зайдите в Yandex Cloud Console")
        print("2. Перейдите в Object Storage")
        print("3. Создайте bucket или используйте существующий")
        print("4. Получите ключи доступа")
        print("\n📝 Введите ваши ключи:")
        
        ya_access_key = input("YA_ACCESS_KEY: ").strip()
        ya_secret_key = input("YA_SECRET_KEY: ").strip()
        bucket_name = input("BUCKET_NAME: ").strip()
        
        if ya_access_key and ya_secret_key and bucket_name:
            os.environ['YA_ACCESS_KEY'] = ya_access_key
            os.environ['YA_SECRET_KEY'] = ya_secret_key
            os.environ['BUCKET_NAME'] = bucket_name
            print("✅ Переменные Yandex S3 настроены!")
        else:
            print("❌ Переменные Yandex S3 не введены")
            return False
    
    return True


def test_connections():
    """Тестирование подключений"""
    print("\n🧪 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЙ")
    print("="*50)
    
    # Тест Supabase
    try:
        from supabase import create_client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            result = supabase.table('tinkoff_operations').select('*').limit(1).execute()
            print("✅ Подключение к Supabase: OK")
        else:
            print("❌ Подключение к Supabase: НЕ НАСТРОЕНО")
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
    
    # Тест Yandex S3
    try:
        import boto3
        from botocore.config import Config
        
        ya_access_key = os.environ.get('YA_ACCESS_KEY')
        ya_secret_key = os.environ.get('YA_SECRET_KEY')
        bucket_name = os.environ.get('BUCKET_NAME')
        
        if ya_access_key and ya_secret_key and bucket_name:
            s3_client = boto3.client(
                service_name="s3",
                aws_access_key_id=ya_access_key,
                aws_secret_access_key=ya_secret_key,
                endpoint_url="https://storage.yandexcloud.net",
                region_name="ru-central1",
                config=Config(signature_version="s3v4"),
            )
            
            # Пытаемся получить список объектов
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            print("✅ Подключение к Yandex S3: OK")
        else:
            print("❌ Подключение к Yandex S3: НЕ НАСТРОЕНО")
    except Exception as e:
        print(f"❌ Ошибка подключения к Yandex S3: {e}")


def run_synchronization():
    """Запуск синхронизации"""
    print("\n🚀 ЗАПУСК СИНХРОНИЗАЦИИ")
    print("="*50)
    
    try:
        # Запускаем скрипт синхронизации
        result = subprocess.run([sys.executable, 's3_to_supabase.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print("📤 Вывод скрипта:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Синхронизация завершена успешно!")
        else:
            print(f"❌ Синхронизация завершилась с ошибкой (код: {result.returncode})")
            
    except Exception as e:
        print(f"❌ Ошибка запуска синхронизации: {e}")


def main():
    """Основная функция"""
    print("🔄 СИНХРОНИЗАЦИЯ S3 → SUPABASE")
    print("="*60)
    
    # Настройка переменных окружения
    if not setup_environment():
        print("\n❌ Не удалось настроить переменные окружения")
        return
    
    # Тестирование подключений
    test_connections()
    
    # Запуск синхронизации
    choice = input("\n🚀 Запустить синхронизацию? (y/n): ").lower()
    if choice in ['y', 'yes', 'да', 'д']:
        run_synchronization()
    else:
        print("⏹️ Синхронизация отменена")
    
    print("\n" + "="*60)
    print("🎯 Готово! Проверьте данные в Supabase SQL Editor")


if __name__ == "__main__":
    main()
