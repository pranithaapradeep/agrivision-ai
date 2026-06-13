from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    organization: Optional[str] = None
    state: Optional[str] = None


class UserLogin(BaseModel):
    username: EmailStr  # OAuth2 form uses 'username'
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    organization: Optional[str]
    state: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Vegetation / Crop Health ─────────────────────────────────────────────────

class VegetationIndexResult(BaseModel):
    ndvi_mean: float
    ndvi_min: float
    ndvi_max: float
    savi_mean: float
    evi_mean: float
    composite_health_score: float


class CropAnalysisCreate(BaseModel):
    field_name: Optional[str] = "Unknown Field"
    crop_type: Optional[str] = "Unknown"
    location: Optional[str] = None
    notes: Optional[str] = None


class CropAnalysisOut(BaseModel):
    id: uuid.UUID
    field_name: str
    crop_type: str
    health_score: float
    health_status: str
    confidence: float
    recommendations: List[str]
    vi_results: Optional[Dict[str, Any]]
    ndvi_colormap_b64: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Soil Analysis ────────────────────────────────────────────────────────────

class SoilAnalysisOut(BaseModel):
    id: uuid.UUID
    field_name: str
    moisture_index: float
    organic_matter_index: float
    nitrogen_index: float
    phosphorus_index: float
    potassium_index: float
    ph_index: float
    salinity_index: float
    erosion_risk: float
    health_score: float
    health_grade: str
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Pest Risk ────────────────────────────────────────────────────────────────

class PestRiskInput(BaseModel):
    field_name: Optional[str] = "Field"
    latitude: float = 20.5937
    longitude: float = 78.9629
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall_mm: Optional[float] = None
    wet_days: Optional[int] = None
    ndvi_score: Optional[float] = None


class PestRiskOut(BaseModel):
    id: uuid.UUID
    field_name: str
    overall_risk_score: float
    risk_level: str
    fungal_risk: float
    insect_risk: float
    bacterial_risk: float
    viral_risk: float
    top_threats: List[Dict[str, Any]]
    recommendations: List[str]
    weather_data: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Forecast ─────────────────────────────────────────────────────────────────

class ForecastInput(BaseModel):
    field_name: Optional[str] = "Field"
    latitude: float = 20.5937
    longitude: float = 78.9629
    historical_days: int = 30


class ForecastDay(BaseModel):
    date: str
    crop_stress: float
    disease_probability: float
    pest_outbreak_risk: float
    confidence: float


class ForecastOut(BaseModel):
    field_name: str
    forecast_days: int
    predictions: List[ForecastDay]
    trend_summary: Dict[str, str]
    alerts: List[str]


# ─── Reports ─────────────────────────────────────────────────────────────────

class ReportCreate(BaseModel):
    field_name: str
    report_type: str = "comprehensive"
    notes: Optional[str] = None
    include_maps: bool = True


class ReportOut(BaseModel):
    id: uuid.UUID
    title: str
    report_type: str
    status: str
    file_path: Optional[str]
    summary: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Alerts ──────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: uuid.UUID
    severity: str
    alert_type: str
    title: str
    message: str
    field_name: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Generic ─────────────────────────────────────────────────────────────────

class HealthCheck(BaseModel):
    status: str
    version: str
    environment: str
    ml_models_loaded: bool
    db_connected: bool
    timestamp: datetime


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
