#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для настройки Git и создания репозитория на GitHub
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Выполнение команды с описанием"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            return True
        else:
            print(f"❌ {description} - ошибка: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False


def setup_git():
    """Настройка Git"""
    print("🔧 НАСТРОЙКА GIT")
    print("="*50)
    
    # Получаем данные пользователя
    print("📝 Введите ваши данные для Git:")
    name = input("Ваше имя: ").strip()
    email = input("Ваш email: ").strip()
    
    if not name or not email:
        print("❌ Имя и email обязательны")
        return False
    
    # Настраиваем Git
    commands = [
        (f'git config user.name "{name}"', "Настройка имени пользователя"),
        (f'git config user.email "{email}"', "Настройка email пользователя"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def create_github_repo():
    """Создание репозитория на GitHub"""
    print("\n🌐 СОЗДАНИЕ РЕПОЗИТОРИЯ НА GITHUB")
    print("="*50)
    
    repo_name = input("Название репозитория (например: tinkoff-supabase-sync): ").strip()
    if not repo_name:
        repo_name = "tinkoff-supabase-sync"
    
    description = input("Описание репозитория (опционально): ").strip()
    
    print(f"\n📋 Инструкции для создания репозитория:")
    print("="*50)
    print("1. Зайдите на https://github.com")
    print("2. Нажмите 'New repository'")
    print(f"3. Название: {repo_name}")
    if description:
        print(f"4. Описание: {description}")
    print("5. Выберите 'Public' или 'Private'")
    print("6. НЕ добавляйте README, .gitignore или лицензию")
    print("7. Нажмите 'Create repository'")
    
    input("\nНажмите Enter когда создадите репозиторий...")
    
    return repo_name


def push_to_github(repo_name):
    """Загрузка в GitHub"""
    print(f"\n🚀 ЗАГРУЗКА В GITHUB")
    print("="*50)
    
    github_username = input("Ваш GitHub username: ").strip()
    if not github_username:
        print("❌ GitHub username обязателен")
        return False
    
    commands = [
        ("git add .", "Добавление файлов"),
        ('git commit -m "🎉 Initial commit: Tinkoff Invest → Supabase sync"', "Создание коммита"),
        (f"git branch -M main", "Переименование ветки в main"),
        (f"git remote add origin https://github.com/{github_username}/{repo_name}.git", "Добавление удаленного репозитория"),
        ("git push -u origin main", "Загрузка в GitHub"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    print(f"\n🎉 Репозиторий создан: https://github.com/{github_username}/{repo_name}")
    return True


def main():
    """Основная функция"""
    print("🚀 СОЗДАНИЕ РЕПОЗИТОРИЯ НА GITHUB")
    print("="*60)
    
    # Проверяем, что мы в Git репозитории
    if not os.path.exists('.git'):
        print("❌ Это не Git репозиторий. Запустите 'git init' сначала.")
        return
    
    # Настраиваем Git
    if not setup_git():
        return
    
    # Создаем репозиторий на GitHub
    repo_name = create_github_repo()
    
    # Загружаем в GitHub
    if not push_to_github(repo_name):
        return
    
    print("\n" + "="*60)
    print("🎉 ГОТОВО!")
    print("="*60)
    print("✅ Git настроен")
    print("✅ Репозиторий создан на GitHub")
    print("✅ Код загружен")
    print("\n💡 Следующие шаги:")
    print("1. Обновите README.md с вашими данными")
    print("2. Добавьте Issues и Wiki если нужно")
    print("3. Настройте GitHub Actions для CI/CD")
    print("4. Пригласите соавторов если нужно")


if __name__ == "__main__":
    main()
