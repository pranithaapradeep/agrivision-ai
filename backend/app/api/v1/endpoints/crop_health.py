"""
Crop Health Analysis API Endpoint
POST /api/v1/crop/analyze  — analyzes uploaded satellite image
GET  /api/v1/crop/analyses — list all analyses for current user
GET  /api/v1/crop/{id}     — get specific analysis
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional, List
import uuid, json
import numpy as np

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.crop import CropAnalysis, VegetationIndex
from app.ml.pipeline.preprocess import ImagePreprocessor
from app.ml.pipeline.vegetation_indices import VegetationIndexEngine
from app.ml.models.cnn_model import CropHealthCNN
from app.ml.pipeline.risk_scoring import RiskScoringEngine

router = APIRouter()
preprocessor     = ImagePreprocessor()
index_engine     = VegetationIndexEngine()
cnn_model        = CropHealthCNN()
risk_engine      = RiskScoringEngine()

class AnalysisResponse(BaseModel):
    id: str
    field_name: str
    crop_type: str
    health_score: float
    health_status: str
    confidence: float
    vegetation_indices: dict
    ndvi_colormap_b64: str
    recommendations: list
    alerts: list

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_crop_health(
    file: UploadFile = File(..., description="Satellite or field image (JPEG/PNG/TIFF)"),
    field_name: str = Form(...),
    crop_type: str = Form(...),
    location_lat: Optional[float] = Form(None),
    location_lon: Optional[float] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ── 1. Read & validate image ─────────────────────────────────────────────
    if file.content_type not in ("image/jpeg", "image/png", "image/tiff", "image/tif"):
        raise HTTPException(400, "Unsupported file type. Upload JPEG, PNG, or TIFF.")
    img_bytes = await file.read()
    if len(img_bytes) > 50 * 1024 * 1024:
        raise HTTPException(400, "File too large. Max 50 MB.")

    # ── 2. Preprocess ────────────────────────────────────────────────────────
    rgb_array = preprocessor.load_from_bytes(img_bytes)
    bands     = preprocessor.simulate_bands_from_rgb(rgb_array)
    nir, red, green, blue = bands["NIR"], bands["Red"], bands["Green"], bands["Blue"]

    # ── 3. Vegetation indices ─────────────────────────────────────────────────
    indices     = index_engine.compute_all(nir, red, blue, green)
    health_score_veg = index_engine.composite_health_score(indices)

    # ── 4. CNN prediction ─────────────────────────────────────────────────────
    cnn_input  = preprocessor.resize_for_cnn(rgb_array)
    cnn_result = cnn_model.predict(cnn_input)

    # ── 5. NDVI colormap for heatmap display ──────────────────────────────────
    ndvi_array  = (indices["NDVI"].mean + 1) / 2  # scalar for now
    ndvi_map    = index_engine.compute_ndvi(nir, red)
    ndvi_raw    = (nir - red) / (nir + red + 1e-8)
    ndvi_img    = preprocessor.generate_ndvi_colormap(ndvi_raw)
    ndvi_b64    = preprocessor.array_to_base64(ndvi_img)

    # ── 6. Risk scoring ──────────────────────────────────────────────────────
    overall_score = health_score_veg * 0.6 + (
        {"healthy": 90, "early_stress": 65, "disease_risk": 40, "severe_stress": 15}
        .get(cnn_result["class"], 50) * 0.4
    )
    alerts = risk_engine.generate_alerts(
        health_score=overall_score,
        pest_risk=30,
        soil_score=60,
        ndvi_mean=indices["NDVI"].mean,
        forecast_trend="stable",
    )
    recommendations = risk_engine.generate_recommendations(
        health_score=overall_score,
        soil_score=60,
        pest_risk=30,
        ndvi_mean=indices["NDVI"].mean,
        humidity=65,
        temperature=28,
    )

    # ── 7. Persist to DB ─────────────────────────────────────────────────────
    analysis = CropAnalysis(
        user_id=current_user.id,
        field_name=field_name,
        crop_type=crop_type,
        location_lat=location_lat,
        location_lon=location_lon,
        overall_health_score=round(overall_score, 2),
        health_status=cnn_result["class"],
        confidence_score=round(cnn_result["confidence"], 4),
        recommendations=[r for r in recommendations],
        analysis_metadata={
            "cnn_result": cnn_result,
            "indices": {k: {"mean": v.mean, "interpretation": v.interpretation}
                        for k, v in indices.items()},
        },
    )
    db.add(analysis)
    await db.flush()

    for name, idx in indices.items():
        vi = VegetationIndex(
            analysis_id=analysis.id,
            index_type=name,
            mean_value=idx.mean,
            min_value=idx.min_val,
            max_value=idx.max_val,
            std_value=idx.std,
            pixel_distribution=idx.histogram,
        )
        db.add(vi)

    await db.commit()
    await db.refresh(analysis)

    return AnalysisResponse(
        id=str(analysis.id),
        field_name=field_name,
        crop_type=crop_type,
        health_score=round(overall_score, 2),
        health_status=cnn_result["class"],
        confidence=round(cnn_result["confidence"], 4),
        vegetation_indices={
            k: {
                "mean": v.mean, "min": v.min_val, "max": v.max_val,
                "std": v.std, "interpretation": v.interpretation,
                "health_score": v.health_score, "histogram": v.histogram
            } for k, v in indices.items()
        },
        ndvi_colormap_b64=ndvi_b64,
        recommendations=[{
            "title": r["title"],
            "description": r["description"],
            "priority": r["priority"],
            "category": r["category"],
        } for r in recommendations],
        alerts=[{
            "type": a["type"],
            "severity": a["severity"],
            "title": a["title"],
            "message": a["message"],
        } for a in alerts],
    )

@router.get("/analyses")
async def list_analyses(
    skip: int = 0, limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CropAnalysis)
        .where(CropAnalysis.user_id == current_user.id)
        .order_by(desc(CropAnalysis.created_at))
        .offset(skip).limit(limit)
    )
    analyses = result.scalars().all()
    return [
        {
            "id": str(a.id), "field_name": a.field_name,
            "crop_type": a.crop_type, "health_score": a.overall_health_score,
            "health_status": a.health_status, "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in analyses
    ]

@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CropAnalysis).where(
            CropAnalysis.id == uuid.UUID(analysis_id),
            CropAnalysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    return {
        "id": str(analysis.id),
        "field_name": analysis.field_name,
        "crop_type": analysis.crop_type,
        "health_score": analysis.overall_health_score,
        "health_status": analysis.health_status,
        "confidence": analysis.confidence_score,
        "metadata": analysis.analysis_metadata,
        "recommendations": analysis.recommendations,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }
