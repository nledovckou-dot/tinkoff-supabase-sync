#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пошаговая инструкция по получению всех ключей
"""

def show_instructions():
    """Показать инструкции по получению ключей"""
    print("🔑 ПОЛУЧЕНИЕ ВСЕХ НЕОБХОДИМЫХ КЛЮЧЕЙ")
    print("="*60)
    
    print("\n1️⃣ ТОКЕН ТИНЬКОФФ (INVEST_TOKEN):")
    print("-" * 40)
    print("• Зайдите в Тинькофф Инвестиции")
    print("• Нажмите на ваш профиль (правый верхний угол)")
    print("• Выберите 'Настройки'")
    print("• Найдите раздел 'API'")
    print("• Нажмите 'Создать токен'")
    print("• Выберите права: 'Чтение'")
    print("• Скопируйте токен (длинная строка)")
    
    print("\n2️⃣ КЛЮЧИ SUPABASE (SUPABASE_KEY):")
    print("-" * 40)
    print("• Зайдите на supabase.com")
    print("• Войдите в ваш проект")
    print("• В левом меню найдите 'Settings' (шестеренка)")
    print("• Нажмите 'API'")
    print("• Найдите раздел 'Project API keys'")
    print("• Скопируйте 'anon public' ключ")
    
    print("\n3️⃣ КЛЮЧИ YANDEX S3:")
    print("-" * 40)
    print("• Зайдите в Yandex Cloud Console (console.cloud.yandex.ru)")
    print("• Перейдите в 'Object Storage'")
    print("• Создайте bucket (если нет):")
    print("  - Нажмите 'Создать bucket'")
    print("  - Введите имя (например: tinkoff-data)")
    print("  - Выберите регион")
    print("• Получите ключи доступа:")
    print("  - Перейдите в 'Service accounts'")
    print("  - Создайте сервисный аккаунт")
    print("  - Создайте статический ключ доступа")
    print("  - Скопируйте Access Key ID и Secret Access Key")
    
    print("\n4️⃣ GOOGLE SHEETS (опционально):")
    print("-" * 40)
    print("• Зайдите в Google Cloud Console")
    print("• Создайте проект или выберите существующий")
    print("• Включите Google Sheets API")
    print("• Создайте сервисный аккаунт")
    print("• Скачайте JSON ключ")
    print("• Создайте Google Sheets таблицу")
    print("• Поделитесь ею с email сервисного аккаунта")
    
    print("\n" + "="*60)
    print("📝 ПОСЛЕ ПОЛУЧЕНИЯ КЛЮЧЕЙ:")
    print("="*60)
    print("1. Откройте файл config.env")
    print("2. Замените шаблоны на реальные значения")
    print("3. Запустите: python3 run_invest.py")


def create_config_template():
    """Создать шаблон конфигурации"""
    print("\n🔧 СОЗДАНИЕ ШАБЛОНА КОНФИГУРАЦИИ")
    print("="*60)
    
    template = """# Конфигурация для синхронизации Тинькофф → S3 → Supabase
# Замените значения на ваши реальные ключи

# Тинькофф (обязательно)
INVEST_TOKEN=ваш_токен_тинькофф_здесь

# Supabase (обязательно)
SUPABASE_URL=https://epqjtskqcbqzaxlusjgf.supabase.co
SUPABASE_KEY=ваш_ключ_supabase_здесь

# Yandex S3 (обязательно)
YA_ACCESS_KEY=ваш_ключ_yandex_здесь
YA_SECRET_KEY=ваш_секретный_ключ_yandex_здесь
BUCKET_NAME=ваше_имя_bucket_здесь

# Google Sheets (опционально)
GSHEETS_SERVICE_ACCOUNT_JSON=ваш_json_ключ_google_здесь
GSHEETS_SPREADSHEET=ваш_id_таблицы_google_здесь
GSHEETS_WORKSHEET=Sheet1

# Дополнительные параметры
DAYS_BACK=1000"""
    
    with open('config_template.env', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ Создан файл config_template.env")
    print("📝 Скопируйте его в config.env и заполните реальными значениями")


if __name__ == "__main__":
    show_instructions()
    create_config_template()
