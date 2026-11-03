# AI Services — лабораторные работы

Код лабораторных работ по дисциплине «Современные интеллектуальные сетевые сервисы» (НИТУ МИСИС). Сервис — агроскоринг: оценка кредитного риска сельскохозяйственных предприятий для банка.

## 1 — Agro Scoring API (FastAPI)

REST API на FastAPI: приём данных хозяйства, валидация (Pydantic), расчёт риска, бизнес-валидация, хранение и выдача результатов.

Файлы: `main.py`, `schemas.py`, `model.py`, `services.py`, `storage.py`.

Endpoints: `GET /health`, `GET /model-info`, `POST /predict`, `GET /predictions/{request_id}`, `GET /predictions`.

Запуск:

```
cd 1
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## 2 — Agro Scoring API: батчинг, очередь, SQLite, LLM

Развитие сервиса из лабы 1: динамический батчинг запросов инференса, очередь с ограничением размера и таймаутом, хранение результатов в SQLite (`aiosqlite`), интеграция с LLM-эндпоинтом для текстовых рекомендаций.

Файл: `main.py`.

Запуск:

```
cd 2
pip install fastapi uvicorn aiosqlite httpx
uvicorn main:app --reload
```

## 3

В разработке.
