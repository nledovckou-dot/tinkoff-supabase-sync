#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Инструкция по получению токена Тинькофф
"""

def show_tinkoff_instructions():
    """Показать инструкции по получению токена Тинькофф"""
    print("🔑 ПОЛУЧЕНИЕ ТОКЕНА ТИНЬКОФФ")
    print("="*60)
    
    print("📱 ПОШАГОВАЯ ИНСТРУКЦИЯ:")
    print("-" * 40)
    print("1. Откройте приложение Тинькофф Инвестиции")
    print("2. Нажмите на ваш профиль (правый верхний угол)")
    print("3. Выберите 'Настройки'")
    print("4. Найдите раздел 'API'")
    print("5. Нажмите 'Создать токен'")
    print("6. Выберите права: 'Чтение'")
    print("7. Скопируйте токен (начинается с 't.')")
    
    print("\n💻 ЧЕРЕЗ ВЕБ-ВЕРСИЮ:")
    print("-" * 40)
    print("1. Зайдите на invest.tinkoff.ru")
    print("2. Войдите в ваш аккаунт")
    print("3. Перейдите в 'Настройки'")
    print("4. Найдите раздел 'API'")
    print("5. Создайте токен для чтения")
    
    print("\n📝 ПРИМЕР ТОКЕНА:")
    print("-" * 40)
    print("Токен выглядит примерно так:")
    print("t.1234567890abcdef1234567890abcdef12345678")
    
    print("\n" + "="*60)
    print("🔧 ПОСЛЕ ПОЛУЧЕНИЯ ТОКЕНА:")
    print("="*60)
    print("1. Откройте файл config.env")
    print("2. Замените строку:")
    print("   INVEST_TOKEN=your_tinkoff_invest_token_here")
    print("   на:")
    print("   INVEST_TOKEN=t.ваш_реальный_токен")
    print("3. Сохраните файл")
    print("4. Запустите: python3 sync_tinkoff_to_supabase.py")
    
    print("\n" + "="*60)
    print("⚠️ ВАЖНО:")
    print("="*60)
    print("• Токен дает доступ к вашим данным")
    print("• Не делитесь им с другими")
    print("• Храните в безопасном месте")
    print("• При необходимости можно отозвать")


def create_test_config():
    """Создать тестовую конфигурацию"""
    print("\n🧪 ТЕСТОВАЯ КОНФИГУРАЦИЯ:")
    print("="*60)
    
    test_config = """# Тестовая конфигурация
INVEST_TOKEN=t.ваш_токен_тинькофф_здесь
SUPABASE_URL=https://epqjtskqcbqzaxlusjgf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVwcWp0c2txY2JxemF4bHVzamdmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODc4Njc2MSwiZXhwIjoyMDc0MzYyNzYxfQ.jgAQylBnCrd0oOhj8vBFU6ZFjQrmwoPgiYPQojJnZiE
DAYS_BACK=1000"""
    
    print(test_config)
    
    print("\n💡 Скопируйте эту конфигурацию в config.env")
    print("   и замените 't.ваш_токен_тинькофф_здесь' на реальный токен")


if __name__ == "__main__":
    show_tinkoff_instructions()
    create_test_config()
