#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Управление ежедневной синхронизацией Тинькофф → Supabase
"""

import os
import subprocess
import sys
from datetime import datetime


def install_daily_sync():
    """Установка ежедневной синхронизации"""
    print("🔧 УСТАНОВКА ЕЖЕДНЕВНОЙ СИНХРОНИЗАЦИИ")
    print("="*60)
    
    plist_file = "com.daily.sync.tinkoff.supabase.plist"
    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
    target_path = os.path.join(launch_agents_dir, plist_file)
    
    try:
        # Копируем plist файл
        subprocess.run(["cp", plist_file, target_path], check=True)
        print(f"✅ Файл скопирован в {target_path}")
        
        # Загружаем LaunchAgent
        subprocess.run(["launchctl", "load", target_path], check=True)
        print("✅ LaunchAgent загружен")
        
        # Проверяем статус
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if "com.daily.sync.tinkoff.supabase" in result.stdout:
            print("✅ Ежедневная синхронизация активна")
            print("🕘 Время запуска: каждый день в 09:00")
        else:
            print("⚠️ LaunchAgent не найден в списке")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        return False


def uninstall_daily_sync():
    """Удаление ежедневной синхронизации"""
    print("🗑️ УДАЛЕНИЕ ЕЖЕДНЕВНОЙ СИНХРОНИЗАЦИИ")
    print("="*60)
    
    plist_file = "com.daily.sync.tinkoff.supabase.plist"
    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
    target_path = os.path.join(launch_agents_dir, plist_file)
    
    try:
        # Выгружаем LaunchAgent
        subprocess.run(["launchctl", "unload", target_path], check=True)
        print("✅ LaunchAgent выгружен")
        
        # Удаляем файл
        if os.path.exists(target_path):
            os.remove(target_path)
            print("✅ Файл удален")
        
        print("✅ Ежедневная синхронизация отключена")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка удаления: {e}")
        return False


def check_status():
    """Проверка статуса синхронизации"""
    print("📊 СТАТУС ЕЖЕДНЕВНОЙ СИНХРОНИЗАЦИИ")
    print("="*60)
    
    try:
        # Проверяем LaunchAgent
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if "com.daily.sync.tinkoff.supabase" in result.stdout:
            print("✅ Ежедневная синхронизация активна")
        else:
            print("❌ Ежедневная синхронизация не активна")
        
        # Проверяем логи
        log_files = [f for f in os.listdir(".") if f.startswith("daily_sync_") and f.endswith(".log")]
        if log_files:
            latest_log = max(log_files)
            print(f"📋 Последний лог: {latest_log}")
            
            # Показываем последние строки лога
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("📄 Последние записи:")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        else:
            print("📋 Лог файлы не найдены")
        
        # Проверяем системные логи
        print("\n🔍 Системные логи:")
        try:
            result = subprocess.run(["tail", "-5", "/tmp/daily-sync.out"], capture_output=True, text=True)
            if result.stdout:
                print("📤 Последний вывод:")
                print(result.stdout)
        except:
            print("📤 Нет системных логов")
        
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")


def run_manual_sync():
    """Ручной запуск синхронизации"""
    print("🔄 РУЧНОЙ ЗАПУСК СИНХРОНИЗАЦИИ")
    print("="*60)
    
    try:
        result = subprocess.run([sys.executable, "daily_sync.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print("📤 Вывод:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Синхронизация завершена успешно")
        else:
            print(f"❌ Синхронизация завершилась с ошибкой (код: {result.returncode})")
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")


def show_schedule():
    """Показать расписание"""
    print("📅 РАСПИСАНИЕ СИНХРОНИЗАЦИИ")
    print("="*60)
    print("🕘 Ежедневно в 09:00")
    print("📊 Получение данных из Тинькофф")
    print("☁️ Загрузка в Yandex S3")
    print("🗄️ Загрузка в Supabase")
    print("📋 Создание лог файла")
    print("="*60)
    print("💡 Для изменения времени отредактируйте plist файл")


def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("🔧 УПРАВЛЕНИЕ ЕЖЕДНЕВНОЙ СИНХРОНИЗАЦИЕЙ")
        print("="*60)
        print("Использование:")
        print("  python3 manage_sync.py install    - Установить ежедневную синхронизацию")
        print("  python3 manage_sync.py uninstall  - Удалить ежедневную синхронизацию")
        print("  python3 manage_sync.py status     - Проверить статус")
        print("  python3 manage_sync.py run        - Запустить синхронизацию вручную")
        print("  python3 manage_sync.py schedule   - Показать расписание")
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_daily_sync()
    elif command == "uninstall":
        uninstall_daily_sync()
    elif command == "status":
        check_status()
    elif command == "run":
        run_manual_sync()
    elif command == "schedule":
        show_schedule()
    else:
        print(f"❌ Неизвестная команда: {command}")


if __name__ == "__main__":
    main()
