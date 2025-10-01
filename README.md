# 🏦 Tinkoff Invest → Supabase Sync

Автоматическая синхронизация данных из Тинькофф Инвестиций в Supabase с промежуточным хранением в Yandex S3.

## 🎯 Возможности

- **Получение данных** из Тинькофф Инвестиций API
- **Загрузка в Yandex S3** для резервного копирования
- **Синхронизация с Supabase** для аналитики и веб-приложений
- **Ежедневное автоматическое обновление** через LaunchAgents
- **Логирование** всех операций
- **Статистика** операций и финансов

## 📊 Архитектура

```
Тинькофф API → CSV → Yandex S3 → Supabase
     ↓              ↓         ↓
  Логирование   Резервная   Веб-приложения
                копия       Аналитика
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте `config_template.env` в `config.env` и заполните реальными значениями:

```bash
cp config_template.env config.env
```

### 3. Получение ключей

#### Тинькофф Инвестиции
1. Зайдите в Тинькофф Инвестиции
2. Настройки → API
3. Создайте токен для чтения
4. Скопируйте токен

#### Supabase
1. Зайдите на [supabase.com](https://supabase.com)
2. Создайте проект
3. Settings → API
4. Скопируйте Project URL и anon public ключ

#### Yandex S3 (опционально)
1. Зайдите в Yandex Cloud Console
2. Object Storage → Создайте bucket
3. Service accounts → Создайте ключи доступа

### 4. Запуск синхронизации

```bash
# Ручной запуск
python3 run_invest_with_env.py  # Тинькофф → S3
python3 upload_to_supabase.py   # S3 → Supabase

# Или полная синхронизация
python3 daily_sync_fixed.py
```

## 🔧 Управление автоматической синхронизацией

### Установка ежедневной синхронизации

```bash
python3 manage_sync.py install
```

### Проверка статуса

```bash
python3 manage_sync.py status
```

### Ручной запуск

```bash
python3 manage_sync.py run
```

### Удаление автоматической синхронизации

```bash
python3 manage_sync.py uninstall
```

## 📁 Структура проекта

```
├── invest.py                    # Основной скрипт синхронизации
├── daily_sync_fixed.py         # Ежедневная синхронизация
├── upload_to_supabase.py       # Загрузка в Supabase
├── manage_sync.py              # Управление автоматизацией
├── run_invest_with_env.py      # Запуск с переменными окружения
├── requirements.txt            # Зависимости Python
├── config_template.env         # Шаблон конфигурации
├── .gitignore                  # Исключения для Git
└── README.md                   # Документация
```

## 📊 Структура данных

### CSV файл содержит:
- `operation_id` - ID операции
- `date_msk` - дата в московском времени
- `action` - тип операции (на русском)
- `amount` - сумма операции
- `currency` - валюта
- `status` - статус операции
- `description` - описание

### Таблица Supabase `tinkoff_operations`:
- `id` - автоинкрементный ID
- `operation_id` - уникальный ID операции
- `date_msk` - дата операции
- `action` - тип операции
- `amount` - сумма операции
- `currency` - валюта
- `status` - статус операции
- `description` - описание
- `created_at` - дата создания записи
- `updated_at` - дата обновления записи

## 🔍 Проверка данных

### В Supabase SQL Editor:
```sql
-- Все операции
SELECT * FROM tinkoff_operations;

-- Операции за последний месяц
SELECT * FROM tinkoff_operations 
WHERE date_msk >= NOW() - INTERVAL '1 month';

-- Сумма всех операций
SELECT SUM(amount) as total_amount FROM tinkoff_operations;

-- Операции по типам
SELECT action, COUNT(*) as count, SUM(amount) as total 
FROM tinkoff_operations 
GROUP BY action;
```

## 📈 Статистика

После каждой синхронизации выводится:
- Количество операций
- Общая сумма
- Количество положительных/отрицательных операций
- Статус загрузки в S3 и Supabase

## 🛠️ Разработка

### Добавление новых источников данных

1. Создайте новый модуль в `sources/`
2. Реализуйте функцию получения данных
3. Добавьте в `daily_sync_fixed.py`

### Расширение функционала Supabase

1. Добавьте новые поля в таблицу
2. Обновите функцию `upload_to_supabase()`
3. Протестируйте с существующими данными

## 🔒 Безопасность

- **Никогда не коммитьте** файл `config.env` с реальными ключами
- **Используйте** `.gitignore` для исключения конфиденциальных данных
- **Регулярно обновляйте** токены доступа
- **Ограничьте права** токенов до минимума

## 📝 Логирование

Все операции логируются в файлы:
- `daily_sync_YYYY-MM-DD.log` - ежедневные логи
- `/tmp/daily-sync.out` - системные логи
- `/tmp/daily-sync.err` - ошибки

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте переменные окружения
2. Проверьте логи синхронизации
3. Убедитесь в доступности API
4. Проверьте права доступа к Supabase

## 📄 Лицензия

MIT License - используйте свободно для личных и коммерческих проектов.

---

**Создано с ❤️ для автоматизации финансового учета**