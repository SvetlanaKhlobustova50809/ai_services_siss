# Лабораторная работа №1. Проектирование AI-сервиса на FastAPI.
# Agro Scoring API — оценка кредитного риска сельскохозяйственных предприятий.

import time
import uuid
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, status

from schemas import FarmRequest, PredictionResponse, HealthResponse, ModelInfoResponse
from model import calculate_risk
from services import risk_level, recommendation, validate_region, validate_risk_level_filter
import storage

# ------------------------------------------------------------
# ЛОГИРОВАНИЕ
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# КОНСТАНТЫ МОДЕЛИ
# ------------------------------------------------------------

MODEL_NAME = "agro-risk-model"
MODEL_VERSION = "1.0"
MODEL_TYPE = "risk-scoring"

# Имитация состояния модели. Если False — /predict вернёт 503.
MODEL_READY = True

# ------------------------------------------------------------
# FASTAPI-ПРИЛОЖЕНИЕ
# ------------------------------------------------------------

app = FastAPI(
    title="Agro Scoring API",
    description="REST API для оценки риска сельскохозяйственных предприятий.",
    version="1.0.0",
)


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    """Измеряет время обработки запроса и добавляет заголовок X-Process-Time."""

    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 6))
    return response


# ------------------------------------------------------------
# GET /health
# ------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Проверка состояния API",
    description="Используется для проверки того, что REST API запущен и отвечает.",
)
def health():
    return {"status": "ok"}


# ------------------------------------------------------------
# GET /model-info
# ------------------------------------------------------------

@app.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Информация о модели",
    description="Возвращает название, версию, тип и текущее состояние модели.",
)
def model_info():
    return {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "model_type": MODEL_TYPE,
        "status": "ready" if MODEL_READY else "unavailable",
    }


# ------------------------------------------------------------
# POST /predict
# ------------------------------------------------------------

@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Оценить риск хозяйства",
    description=(
        "Принимает характеристики хозяйства, выполняет валидацию, "
        "инференс модели, сохраняет и возвращает оценку риска."
    ),
)
def predict(request: FarmRequest):
    # 1. Доступность модели
    if not MODEL_READY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is temporarily unavailable",
        )

    # 2. Бизнес-валидация (Pydantic уже проверил типы, обязательность, диапазоны)
    validate_region(request.region)

    logger.info("Prediction request received | farm_id=%s", request.farm_id)

    # 3. Инференс и постпроцессинг
    score = calculate_risk(request)
    level = risk_level(score)

    # 4. Формирование и сохранение результата
    request_id = str(uuid.uuid4())
    result = {
        "request_id": request_id,
        "farm_id": request.farm_id,
        "risk_score": score,
        "risk_level": level,
        "recommendation": recommendation(level),
        "model_version": MODEL_VERSION,
    }
    storage.save_prediction(request_id, result)

    logger.info(
        "Prediction completed | request_id=%s | farm_id=%s | risk_score=%s | risk_level=%s",
        request_id,
        request.farm_id,
        score,
        level,
    )

    return result


# ------------------------------------------------------------
# GET /predictions
# Должен быть объявлен ДО /predictions/{request_id},
# иначе FastAPI попытается сопоставить "predictions" с path-параметром request_id.
# ------------------------------------------------------------

@app.get(
    "/predictions",
    response_model=list[PredictionResponse],
    summary="Получить список прогнозов",
    description="Возвращает список выполненных прогнозов с ограничением количества и фильтрацией по уровню риска.",
)
def get_predictions(
    limit: int = Query(default=10, ge=1, le=100, description="Максимальное количество результатов"),
    risk_level: Optional[str] = Query(default=None, description="Фильтр по категории риска: low, medium или high"),
):
    if risk_level is not None:
        validate_risk_level_filter(risk_level)

    return storage.list_predictions(risk_level=risk_level, limit=limit)


# ------------------------------------------------------------
# GET /predictions/{request_id}
# ------------------------------------------------------------

@app.get(
    "/predictions/{request_id}",
    response_model=PredictionResponse,
    summary="Получить прогноз по request_id",
    description="Возвращает сохранённый прогноз по его уникальному идентификатору.",
)
def get_prediction(request_id: str):
    result = storage.get_prediction(request_id)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
