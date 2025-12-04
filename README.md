# Django API Demo Project

Демонстрационный проект Django REST API для управления заявками на выплату средств с использованием Celery для фоновых задач.

## Описание проекта

Проект представляет собой RESTful API для работы с заявками на выплату средств. Основные возможности:

- Создание, просмотр, обновление и удаление заявок на выплату
- Поддержка нескольких валют (RUB, USD, EUR, GBP)
- Отслеживание статусов заявок (ожидание, обработка, одобрено, отклонено, выполнено, отменено)
- Асинхронная обработка заявок с помощью Celery
- REST API с документацией (drf-spectacular)
- PostgreSQL в качестве СУБД
- RabbitMQ для очереди задач
- Nginx в качестве reverse proxy

## Технологический стек

- Python 3.12+
- Django 5.2
- Django REST Framework 3.15
- PostgreSQL 15
- Celery 5.3
- RabbitMQ 3.10
- Nginx 1.21
- Docker & Docker Compose
- Gunicorn

## Структура проекта

```
demo_django_api/
├── requests_app/              # Основное Django приложение
│   ├── config/                # Настройки проекта
│   │   ├── components/        # Модульные настройки (split-settings)
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── celery.py
│   ├── request/               # Приложение для работы с заявками
│   │   ├── api/               # API endpoints
│   │   │   └── v1/            # API версии 1
│   │   ├── models.py          # Модели данных
│   │   ├── signals.py         # Django signals
│   │   ├── tasks.py           # Celery tasks
│   │   ├── tests/             # Тесты
│   │   └── fixtures/          # Тестовые данные
│   ├── manage.py
│   └── gunicorn.conf.py
├── nginx/                     # Конфигурация Nginx
├── docker-compose.yml         # Docker Compose конфигурация
├── Makefile                   # Makefile с командами для разработки
└── pyproject.toml             # Зависимости проекта (uv)
```

## Требования для локального запуска

- Python 3.12 или выше
- PostgreSQL 15
- RabbitMQ 3.10
- uv (установка: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Запуск локально (без Docker)

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd demo_django_api
```

### 2. Создание виртуального окружения и установка зависимостей

```bash
# uv автоматически создаст виртуальное окружение
uv sync
```

### 3. Настройка переменных окружения

Создайте файлы `.env.backend` и `.env.db` на основе примеров:

```bash
cp .env.backend.example .env.backend
cp .env.db.example .env.db
```

Отредактируйте файлы, указав необходимые параметры подключения к базе данных и другие настройки.

### 4. Запуск PostgreSQL и RabbitMQ

Убедитесь, что PostgreSQL и RabbitMQ запущены локально или используйте Docker для их запуска:

```bash
# Запуск только базы данных и RabbitMQ
docker-compose up -d db rabbitmq
```

### 5. Применение миграций

```bash
cd requests_app
uv run python manage.py migrate
```

### 6. Создание суперпользователя (опционально)

```bash
uv run python manage.py createsuperuser
```

### 7. Загрузка тестовых данных (опционально)

```bash
uv run python manage.py loaddata payment_requests
```

### 8. Запуск сервера разработки

```bash
uv run python manage.py runserver
```

API будет доступен по адресу: `http://localhost:8000/`

### 9. Запуск Celery worker (в отдельном терминале)

```bash
cd requests_app
uv run celery -A config worker --loglevel=info
```

### 10. Запуск Celery beat (в отдельном терминале, если нужны периодические задачи)

```bash
cd requests_app
uv run celery -A config beat --loglevel=info
```

## Запуск через Docker Compose

Docker Compose запускает все сервисы (PostgreSQL, RabbitMQ, Django, Celery, Nginx) в контейнерах.

### 1. Настройка переменных окружения

```bash
cp .env.backend.example .env.backend
cp .env.db.example .env.db
```

Отредактируйте файлы при необходимости.

### 2. Сборка образов

```bash
make build
```

или

```bash
docker-compose build
```

### 3. Запуск всех сервисов

```bash
make start
```

или

```bash
docker-compose up -d
```

API будет доступен по адресу: `http://localhost/`

### 4. Просмотр логов

```bash
make logs
```

или

```bash
docker-compose logs -f
```

### 5. Просмотр статуса сервисов

```bash
make status
```

или

```bash
docker-compose ps
```

### 6. Остановка сервисов

```bash
make stop
```

или

```bash
docker-compose down
```

### 7. Перезапуск сервисов

```bash
make restart
```

### 8. Полная очистка (удаление контейнеров, volumes, образов)

```bash
make clean
```

или

```bash
docker-compose down -v --rmi all --remove-orphans
```

## Тестирование

### Запуск тестов локально

```bash
cd requests_app
uv run pytest
```

### Запуск тестов с покрытием

```bash
cd requests_app
uv run pytest --cov=request --cov-report=html
```

### Запуск тестов в Docker контейнере

```bash
docker-compose exec backend uv run pytest
```

### Запуск конкретного теста

```bash
cd requests_app
uv run pytest request/tests/test_api.py::TestPaymentRequestAPI::test_create_payment_request
```

### Проверка кода линтерами

```bash
# Flake8
uv run flake8 requests_app/

# Black (форматирование)
uv run black requests_app/ --check

# Black (автоформатирование)
uv run black requests_app/

# Bandit (проверка безопасности)
uv run bandit -r requests_app/
```

## API Endpoints

Основные эндпоинты API:

- `GET /api/v1/payouts/` - Список всех заявок на выплату
- `POST /api/v1/payouts/` - Создание новой заявки
- `GET /api/v1/payouts/{id}/` - Получение конкретной заявки
- `PUT /api/v1/payouts/{id}/` - Обновление заявки
- `PATCH /api/v1/payouts/{id}/` - Частичное обновление заявки
- `DELETE /api/v1/payouts/{id}/` - Удаление заявки

Документация API доступна по адресам:
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`
- OpenAPI Schema: `/api/schema/`

## Пример запроса к API

### Создание заявки на выплату

```bash
curl -X POST http://localhost/api/v1/payouts/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "7000.00",
    "currency": "RUB",
    "recipient_name": "Иванов Иван Иванович",
    "recipient_account": "40817810099910001234",
    "recipient_bank": "Сбербанк России",
    "recipient_bank_code": "044525225",
    "description": "Тестовая выплата"
  }'
```

или используйте команду Makefile:

```bash
make test-api
```

### Получение списка заявок

```bash
curl http://localhost/api/v1/payouts/
```

## Полезные команды

Makefile содержит полезные команды для работы с проектом:

```bash
make help       # Показать все доступные команды
make build      # Собрать Docker образы
make start      # Запустить все сервисы
make stop       # Остановить все сервисы
make restart    # Перезапустить все сервисы
make logs       # Просмотр логов
make status     # Статус сервисов
make clean      # Полная очистка
make test-api   # Тестовый запрос к API
```

## Доступ к админ-панели Django

После создания суперпользователя админ-панель доступна по адресу:
- Локально: `http://localhost:8000/admin/`
- Docker: `http://localhost/admin/`

## Доступ к RabbitMQ Management

RabbitMQ Management UI доступен по адресу:
- `http://localhost:15672/`
- Логин: `guest`
- Пароль: `guest`

## Troubleshooting

### Проблема: Порт уже занят

Если порты 80, 5432 или 5672 заняты другими приложениями, измените их в `docker-compose.yml`:

```yaml
ports:
  - "8080:80"  # Вместо 80:80
```

### Проблема: База данных не готова

Если при запуске возникают ошибки подключения к базе данных, дождитесь полной инициализации PostgreSQL (healthcheck в docker-compose).

### Проблема: Миграции не применены

Выполните миграции вручную:

```bash
docker-compose exec backend uv run python manage.py migrate
```

## Разработка

### Pre-commit hooks

Проект использует pre-commit hooks для проверки кода перед коммитом:

```bash
# Установка pre-commit hooks
uv run pre-commit install

# Запуск проверки вручную
uv run pre-commit run --all-files
```

### CI/CD

Проект использует GitHub Actions для автоматической проверки кода. Конфигурация находится в `.github/workflows/code-checker.yaml`.

## Лицензия

MIT

## Контакты

Для вопросов и предложений создавайте issues в репозитории проекта.

Скриншоты:
## Админ панель
<img width="1449" height="872" alt="image" src="https://github.com/user-attachments/assets/866434d5-116f-42f6-a69b-e37106a5a8ff" />

## API
<img width="1418" height="899" alt="image" src="https://github.com/user-attachments/assets/bc039c7c-5277-41b3-9121-bd9787d3d981" />

## Celery task worker
<img width="1492" height="764" alt="image" src="https://github.com/user-attachments/assets/459ee333-c1ed-4a2b-beff-8d8c54b6e138" />

## CI/CD 
базовый настроен, запуск линтера - тестов, далее можно развивать (нотификации и тп)

