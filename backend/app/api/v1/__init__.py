from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, upload, crop_health, soil, pest, forecast, reports
)

router = APIRouter()
router.include_router(auth.router,        prefix="/auth",     tags=["Authentication"])
router.include_router(upload.router,      prefix="/upload",   tags=["Upload"])
router.include_router(crop_health.router, prefix="/crop",     tags=["Crop Health"])
router.include_router(soil.router,        prefix="/soil",     tags=["Soil Analysis"])
router.include_router(pest.router,        prefix="/pest",     tags=["Pest Risk"])
router.include_router(forecast.router,    prefix="/forecast", tags=["Forecasting"])
router.include_router(reports.router,     prefix="/reports",  tags=["Reports"])
