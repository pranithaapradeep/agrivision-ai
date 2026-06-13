from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.ml.models.rf_model import PestRiskRF
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from app.core.config import settings

router = APIRouter()
rf_model = PestRiskRF()

class PestRiskRequest(BaseModel):
    crop_type: str
    field_name: str
    location_lat: Optional[float] = 20.5937   # Default: India center
    location_lon: Optional[float] = 78.9629
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall_7d: Optional[float] = None
    consecutive_wet_days: Optional[float] = 0
    wind_speed: Optional[float] = None
    ndvi: Optional[float] = 0.45
    ndvi_trend_7d: Optional[float] = 0.0
    soil_moisture: Optional[float] = 40.0
    crop_age_days: Optional[float] = 45.0
    previous_pest_incidence: Optional[float] = 0.1

async def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch live weather from OpenWeatherMap API."""
    if settings.OPENWEATHER_API_KEY == "demo_key":
        # Return realistic demo data for hackathon
        return {
            "temperature": 28.5,
            "humidity": 72.0,
            "wind_speed": 12.0,
            "rainfall_7d": 18.5,
        }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY, "units": "metric"},
            )
            data = r.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "rainfall_7d": data.get("rain", {}).get("1h", 0) * 168,
            }
    except Exception:
        return {"temperature": 28.5, "humidity": 72.0, "wind_speed": 12.0, "rainfall_7d": 18.5}

@router.post("/assess")
async def assess_pest_risk(
    req: PestRiskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    weather = await fetch_weather(req.location_lat, req.location_lon)

    features = {
        "temperature":             req.temperature or weather["temperature"],
        "humidity":                req.humidity    or weather["humidity"],
        "rainfall_7d":             req.rainfall_7d or weather["rainfall_7d"],
        "consecutive_wet_days":    req.consecutive_wet_days,
        "wind_speed":              req.wind_speed  or weather["wind_speed"],
        "ndvi":                    req.ndvi,
        "ndvi_trend_7d":           req.ndvi_trend_7d,
        "soil_moisture":           req.soil_moisture,
        "crop_age_days":           req.crop_age_days,
        "previous_pest_incidence": req.previous_pest_incidence,
    }

    result = rf_model.predict(features)

    return {
        "field_name":         req.field_name,
        "crop_type":          req.crop_type,
        "overall_risk_score": result.overall_risk_score,
        "risk_level":         result.risk_level,
        "fungal_risk":        result.fungal_risk,
        "insect_risk":        result.insect_risk,
        "bacterial_risk":     result.bacterial_risk,
        "viral_risk":         result.viral_risk,
        "top_threats":        result.top_threats,
        "recommendations":    result.recommendations,
        "weather_used":       weather,
    }

@router.get("/demo-heatmap")
async def get_demo_heatmap(
    current_user: User = Depends(get_current_user)
):
    """
    Returns synthetic geospatial heatmap data for pest risk visualization.
    Represents a grid over an Indian agricultural region.
    """
    import random, math
    random.seed(42)
    points = []
    # Generate 200 risk points around a central Indian farm location
    center_lat, center_lon = 20.5937, 78.9629
    for _ in range(200):
        lat = center_lat + random.uniform(-0.3, 0.3)
        lon = center_lon + random.uniform(-0.3, 0.3)
        # Cluster high-risk zones
        dist = math.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
        base_risk = max(0, 80 - dist * 150 + random.gauss(0, 10))
        points.append({
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "risk_score": round(min(100, max(0, base_risk)), 1),
        })
    return {"heatmap_points": points, "center": {"lat": center_lat, "lon": center_lon}}
