# Постпроцессинг предсказаний и бизнес-валидация (правила, не проверяемые Pydantic)

from fastapi import HTTPException, status

ALLOWED_REGIONS = {"Krasnodar", "Rostov", "Stavropol"}
ALLOWED_RISK_LEVELS = {"low", "medium", "high"}


def risk_level(score: float) -> str:
    """Преобразует числовой risk_score в категорию риска."""

    if score < 0.3:
        return "low"
    if score < 0.7:
        return "medium"
    return "high"


def recommendation(level: str) -> str:
    """Возвращает рекомендацию оператору банка в зависимости от категории риска."""

    if level == "low":
        return "Стандартное рассмотрение"
    if level == "medium":
        return "Требуется дополнительная проверка"
    return "Высокий риск. Требуется ручное рассмотрение"


def validate_region(region: str) -> None:
    """Бизнес-ограничение: регион должен входить в список обслуживаемых банком."""

    if region not in ALLOWED_REGIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown region: {region}. Allowed regions: {sorted(ALLOWED_REGIONS)}",
        )


def validate_risk_level_filter(value: str) -> None:
    """Бизнес-ограничение: фильтр risk_level в /predictions должен быть известным значением."""

    if value not in ALLOWED_RISK_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="risk_level must be 'low', 'medium' or 'high'",
        )
