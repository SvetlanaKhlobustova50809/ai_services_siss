# Временное хранилище результатов прогнозов (в оперативной памяти).
# Позже может быть заменено на PostgreSQL / SQLite без изменения контракта API.

from typing import Dict, List, Optional

predictions: Dict[str, dict] = {}


def save_prediction(request_id: str, result: dict) -> None:
    predictions[request_id] = result


def get_prediction(request_id: str) -> Optional[dict]:
    return predictions.get(request_id)


def list_predictions(risk_level: Optional[str] = None, limit: int = 10) -> List[dict]:
    values = list(predictions.values())

    if risk_level is not None:
        values = [item for item in values if item["risk_level"] == risk_level]

    return values[:limit]
