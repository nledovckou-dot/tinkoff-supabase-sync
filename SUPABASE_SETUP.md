# 🚀 БЫСТРЫЙ СТАРТ - Настройка Supabase

## 1. Создание проекта Supabase

1. Зайдите на [supabase.com](https://supabase.com)
2. Нажмите "New Project"
3. Выберите организацию
4. Введите название проекта (например: "tinkoff-invest")
5. Выберите регион (рекомендуется: Europe)
6. Введите пароль для базы данных
7. Нажмите "Create new project"

## 2. Получение ключей

1. В панели проекта перейдите в **Settings** → **API**
2. Скопируйте:
   - **Project URL** (например: `https://abcdefgh.supabase.co`)
   - **anon public** ключ (длинная строка)

## 3. Настройка переменных окружения

```bash
# Supabase
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your_supabase_anon_key

# Yandex S3 (если есть)
export YA_ACCESS_KEY=your_yandex_access_key
export YA_SECRET_KEY=your_yandex_secret_key
export BUCKET_NAME=your_bucket_name
```

## 4. Тестирование подключения

```bash
python test_supabase.py
```

## 5. Запуск синхронизации

```bash
python s3_to_supabase.py
```

## 6. Проверка данных

1. Зайдите в панель Supabase
2. Перейдите в **Table Editor**
3. Найдите таблицу `tinkoff_operations`
4. Проверьте загруженные данные

## 🎯 Готово!

Теперь ваши данные из Тинькофф банка автоматически синхронизируются с Supabase!
