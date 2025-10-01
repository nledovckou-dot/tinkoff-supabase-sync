# 🚀 Быстрое создание репозитория на GitHub

## 📋 Что нужно сделать:

### 1. Настройте Git (если еще не настроен)
```bash
git config --global user.name "Ваше Имя"
git config --global user.email "ваш@email.com"
```

### 2. Создайте репозиторий на GitHub
1. Зайдите на [github.com](https://github.com)
2. Нажмите **"New repository"**
3. Название: `tinkoff-supabase-sync`
4. Описание: `Автоматическая синхронизация данных из Тинькофф Инвестиций в Supabase`
5. Выберите **Public** или **Private**
6. **НЕ** добавляйте README, .gitignore или лицензию
7. Нажмите **"Create repository"**

### 3. Загрузите код в GitHub
```bash
# Добавьте все файлы
git add .

# Создайте коммит
git commit -m "🎉 Initial commit: Tinkoff Invest → Supabase sync"

# Переименуйте ветку в main
git branch -M main

# Добавьте удаленный репозиторий (замените YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/tinkoff-supabase-sync.git

# Загрузите код
git push -u origin main
```

### 4. Проверьте результат
Зайдите на ваш репозиторий: `https://github.com/YOUR_USERNAME/tinkoff-supabase-sync`

## 🔒 Важно!

- **НЕ загружайте** файл `config.env` с реальными ключами
- **Используйте** `config_template.env` как шаблон
- **Добавьте** `.gitignore` для исключения конфиденциальных данных

## 📝 После создания репозитория:

1. **Обновите README.md** с вашими данными
2. **Добавьте описание** проекта
3. **Настройте Issues** для багов и предложений
4. **Создайте Wiki** с подробной документацией
5. **Добавьте лицензию** (MIT рекомендуется)

## 🎯 Готово!

Теперь у вас есть публичный репозиторий с полным проектом синхронизации Тинькофф → Supabase!
