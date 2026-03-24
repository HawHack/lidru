# RATING PLATFORM

Веб-платформа для учета активности участников молодежного парламента и кадрового резерва.

## ВОЗМОЖНОСТИ ПРОЕКТА
- Регистрация и авторизация пользователей
- Роли: участник, организатор, наблюдатель (кадровая служба)
- Создание мероприятий организаторами
- Запись участников на мероприятия
- Подтверждение участия организатором
- Начисление баллов
- Глобальный рейтинг участников
- Профиль участника с портфолио и уровнями
- Профиль организатора с отзывами и рейтингом доверия
- Дашборд активности
- Страница кадрового инспектора с фильтрами
- Отчет по кандидату
- Простая QR-ready check-in логика
- Django Admin для управления данными

## ТЕХНОЛОГИИ
- Python 3.11+
- Django 5.1.7
- SQLite
- Bootstrap 5
- Chart.js

## УСТАНОВКА И ЗАПУСК

### Вариант 1: Через командную строку (CMD)

1. Клонировать репозиторий
   ```
   git clone https://github.com/HawHack/lidru
   cd lidru
   ```

2. Создать виртуальное окружение

   Windows PowerShell:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   Если PowerShell блокирует активацию:
   ```
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

   Windows Command Prompt:
   ```
   python -m venv venv
   venv\Scripts\activate.bat
   ```

3. Установить зависимости
   ```
   pip install -r requirements.txt
   ```

4. Применить миграции
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Создать суперпользователя
   ```
   python manage.py createsuperuser
   ```

6. Загрузить тестовые данные в БД
   ```
   python manage.py seed_data
   ```

7. Запустить сервер
   ```
   python manage.py runserver
   ```

### Вариант 2: Через Docker

1. Убедитесь, что Docker установлен и запущен.

2. Клонировать репозиторий
   ```
   git clone https://github.com/HawHack/lidru
   cd lidru
   ```
3. Запустите приложение:
   ```
   docker-compose up
   ```
4. Загрузить тестовые данные в БД (Ввод через терминал докера после запуска)
   ```
   python manage.py seed_data
   ```



## ПОСЛЕ ЗАПУСКА

Сайт: http://127.0.0.1:8000/ (или http://localhost:8000/ для Docker)

Админка: http://127.0.0.1:8000/admin/

## ТЕСТОВЫЕ АККАУНТЫ (после seed_data)
- Организатор: organizer1 / 12345678Qq
- Участник: participant1 / 12345678Qq
- Наблюдатель: observer1 / 12345678Qq

## ОСНОВНЫЕ СТРАНИЦЫ
- Главная: /
- Мероприятия: /events/
- Рейтинг: /ratings/
- Профиль: /users/profile/
- Инспектор кадрового резерва: /inspector/

## Структура проекта
- `config/` - Настройки Django
- `dashboard/` - Дашборд приложения
- `events/` - Управление событиями
- `ratings/` - Система рейтингов
- `users/` - Управление пользователями
- `static/` - Статические файлы (CSS)
- `templates/` - HTML шаблоны

## Лицензия
Этот проект открыт для использования.
Инспектор кадрового резерва: /inspector/
