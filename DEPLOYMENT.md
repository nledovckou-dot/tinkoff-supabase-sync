# 🚀 Инструкция по развертыванию

## 📋 Предварительные требования

- Python 3.7+
- Git
- Аккаунт на GitHub
- Токен Тинькофф Инвестиций
- Проект Supabase
- Yandex S3 (опционально)

## 🔧 Пошаговая настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/tinkoff-supabase-sync.git
cd tinkoff-supabase-sync
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

```bash
cp config_template.env config.env
# Отредактируйте config.env с вашими ключами
```

### 4. Получение ключей

#### Тинькофф Инвестиции
1. Откройте приложение Тинькофф Инвестиции
2. Перейдите в Настройки → API
3. Создайте токен для чтения
4. Скопируйте токен в `config.env`

#### Supabase
1. Зайдите на [supabase.com](https://supabase.com)
2. Создайте новый проект
3. Перейдите в Settings → API
4. Скопируйте Project URL и anon public ключ

#### Yandex S3 (опционально)
1. Зайдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте bucket в Object Storage
3. Создайте сервисный аккаунт
4. Получите ключи доступа

### 5. Тестирование

```bash
# Тест подключения к Supabase
python3 test_supabase_only.py

# Тест полной синхронизации
python3 daily_sync_fixed.py
```

### 6. Настройка автоматизации

```bash
# Установка ежедневной синхронизации
python3 manage_sync.py install

# Проверка статуса
python3 manage_sync.py status
```

## 🔍 Проверка работы

### В Supabase SQL Editor:
```sql
SELECT COUNT(*) FROM tinkoff_operations;
SELECT * FROM tinkoff_operations LIMIT 5;
```

### Проверка логов:
```bash
ls -la daily_sync_*.log
tail -f daily_sync_$(date +%Y-%m-%d).log
```

## 🛠️ Устранение неполадок

### Ошибка аутентификации Тинькофф
- Проверьте токен в `config.env`
- Убедитесь, что токен имеет права на чтение

### Ошибка подключения к Supabase
- Проверьте URL и ключ в `config.env`
- Убедитесь, что проект Supabase активен

### Ошибка загрузки в S3
- Проверьте ключи доступа Yandex S3
- Убедитесь, что bucket существует

### LaunchAgent не работает
```bash
# Проверка статуса
launchctl list | grep tinkoff

# Перезагрузка
python3 manage_sync.py uninstall
python3 manage_sync.py install
```

## 📊 Мониторинг

### Ежедневные проверки
1. Проверьте логи синхронизации
2. Убедитесь, что данные обновились в Supabase
3. Проверьте статус LaunchAgent

### Еженедельные проверки
1. Проверьте актуальность токенов
2. Очистите старые лог файлы
3. Проверьте доступность API

## 🔄 Обновление

```bash
git pull origin main
pip install -r requirements.txt
```

## 🗑️ Удаление

```bash
# Остановка автоматической синхронизации
python3 manage_sync.py uninstall

# Удаление репозитория
rm -rf tinkoff-supabase-sync
```
