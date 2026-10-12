# Inventory Management API

Учебный REST API для управления складскими товарами. Проект демонстрирует базовые backend-задачи: HTTP-эндпоинты, CRUD-операции, валидацию данных, SQLite, обработку ошибок и автоматические тесты.

## Технологии

- Python 3.10+
- FastAPI
- SQLite (`sqlite3`, встроен в Python)
- Pydantic
- pytest и HTTPX для тестирования

## Возможности

- Создание товара.
- Получение одного товара по ID.
- Просмотр списка товаров с поиском по названию или SKU.
- Пагинация через `limit` и `offset`.
- Частичное обновление товара.
- Удаление товара.
- Проверка уникальности SKU.
- Валидация количества и цены.
- Понятные HTTP-ошибки (`404`, `409`, `422`).
- Документация API через Swagger UI.

## Запуск локально

Требуется Python 3.10 или новее.

### 1. Создать виртуальное окружение

Windows:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
python -m pip install -r requirements.txt
```

### 3. Запустить сервер

Из корневой папки проекта:

```bash
uvicorn app.main:app --reload
```

После запуска:
- API: http://127.0.0.1:8000
- Интерактивная документация: http://127.0.0.1:8000/docs
- Альтернативная документация: http://127.0.0.1:8000/redoc
- Проверка состояния: http://127.0.0.1:8000/health

База данных автоматически создаётся в `data/inventory.db`. Для другого пути можно задать переменную окружения `DATABASE_PATH`.

## Примеры запросов

### Создать товар

```bash
curl -X POST "http://127.0.0.1:8000/products" \
  -H "Content-Type: application/json" \
  -d '{"name":"Mechanical Keyboard","sku":"KB-001","quantity":12,"price":79.99,"description":"Compact keyboard"}'
```

### Получить список

```bash
curl "http://127.0.0.1:8000/products?limit=20&offset=0"
```

### Найти товар по названию или SKU

```bash
curl "http://127.0.0.1:8000/products?search=Keyboard"
```

### Обновить количество

```bash
curl -X PATCH "http://127.0.0.1:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{"quantity":7}'
```

### Удалить товар

```bash
curl -X DELETE "http://127.0.0.1:8000/products/1"
```

## API endpoints

| Method | Endpoint | Описание |
|---|---|---|
| GET | `/health` | Проверка состояния |
| POST | `/products` | Создать товар |
| GET | `/products` | Список товаров; `search`, `limit`, `offset` |
| GET | `/products/{product_id}` | Получить товар |
| PATCH | `/products/{product_id}` | Частично обновить товар |
| DELETE | `/products/{product_id}` | Удалить товар |

## Запуск тестов

```bash
python -m pytest
```

Тесты проверяют основные сценарии API: создание и получение товара, поиск и пагинацию, обновление, удаление, валидацию, дубликаты SKU и ответы для несуществующих товаров. Тестовая база создаётся во временной директории и не изменяет рабочую базу данных.

## Структура проекта

```text
inventory_management_api/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
├── tests/
│   └── test_api.py
├── examples/
├── data/                  # создаётся автоматически при запуске
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Возможные следующие улучшения

- Аутентификация пользователей и роли доступа.
- Учёт движений товара и история изменений.
- Миграции схемы базы данных.
- Docker и CI для автоматического запуска тестов.
- Более подробное логирование.

