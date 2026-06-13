from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.ml.models.lstm_model import CropStressLSTM
from sqlalchemy.ext.asyncio import AsyncSession
import random, math
from datetime import date, timedelta

router = APIRouter()
lstm = CropStressLSTM()

class HistoryPoint(BaseModel):
    ndvi: float = 0.45
    evi: float = 0.38
    savi: float = 0.40
    temperature: float = 28.0
    humidity: float = 65.0
    rainfall_mm: float = 5.0
    soil_moisture: float = 40.0
    wet_days_consecutive: float = 1.0

class ForecastRequest(BaseModel):
    history: Optional[List[HistoryPoint]] = None
    target: str = "stress_score"     # stress_score | disease_prob | pest_prob

@router.post("/predict")
async def get_forecast(
    req: ForecastRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history_dicts = [h.dict() for h in req.history] if req.history else _generate_demo_history()
    result = lstm.forecast(history_dicts, target=req.target)
    return {
        "metric":                   result.metric,
        "current_value":            result.current_value,
        "forecast_values":          result.forecast_values,
        "forecast_dates":           result.forecast_dates,
        "trend":                    result.trend,
        "confidence_interval_upper":result.confidence_interval_upper,
        "confidence_interval_lower":result.confidence_interval_lower,
        "alert_triggered":          result.alert_triggered,
        "alert_message":            result.alert_message,
    }

@router.get("/demo")
async def get_demo_forecast(current_user: User = Depends(get_current_user)):
    """Returns multi-metric forecast for dashboard demo."""
    history = _generate_demo_history()
    results = {}
    for target in ["stress_score", "disease_prob", "pest_prob"]:
        r = lstm.forecast(history, target=target)
        results[target] = {
            "current_value":   r.current_value,
            "forecast_values": r.forecast_values,
            "forecast_dates":  r.forecast_dates,
            "trend":           r.trend,
            "ci_upper":        r.confidence_interval_upper,
            "ci_lower":        r.confidence_interval_lower,
        }
    return results

def _generate_demo_history():
    """Generate 30-day synthetic history for demo."""
    random.seed(123)
    history = []
    for i in range(30):
        ndvi = 0.55 - i * 0.005 + random.gauss(0, 0.02)
        history.append({
            "ndvi":                 max(0.1, ndvi),
            "evi":                  max(0.05, ndvi - 0.08),
            "savi":                 max(0.05, ndvi - 0.05),
            "temperature":          28 + 3 * math.sin(i / 7) + random.gauss(0, 1),
            "humidity":             65 + 10 * math.sin(i / 5) + random.gauss(0, 3),
            "rainfall_mm":          max(0, random.gauss(5, 8)),
            "soil_moisture":        max(20, 45 - i * 0.3 + random.gauss(0, 2)),
            "wet_days_consecutive": max(0, min(7, int(random.gauss(1.5, 1.2)))),
        })
    return history
