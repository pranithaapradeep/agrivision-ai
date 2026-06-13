from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

router = APIRouter()

@router.post("/analyze")
async def analyze_soil(
    file: UploadFile = File(...),
    field_name: str = Form(...),
    crop_type: str = Form(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Estimates soil properties from satellite spectral reflectance.
    Uses SWIR/NIR band ratios as proxies for soil moisture and organic matter.
    """
    from app.ml.pipeline.preprocess import ImagePreprocessor
    preprocessor = ImagePreprocessor()

    img_bytes = await file.read()
    rgb = preprocessor.load_from_bytes(img_bytes)
    bands = preprocessor.simulate_bands_from_rgb(rgb)

    nir, red, green, blue = bands["NIR"], bands["Red"], bands["Green"], bands["Blue"]

    # Soil moisture index: uses NIR and SWIR approximation
    swir_approx = np.clip(red * 0.9 + blue * 0.1, 0, 1)
    moisture_idx = float(np.mean((nir - swir_approx) / (nir + swir_approx + 1e-8)))
    moisture_pct = round(np.clip((moisture_idx + 1) / 2 * 80, 10, 85), 2)

    # Organic matter proxy: dark soils appear darker (low reflectance)
    brightness = float(np.mean(0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]) / 255)
    organic_matter = round(max(0.5, min(8.0, (1 - brightness) * 10)), 2)

    # Soil health score composite
    ndvi_mean = float(np.mean((nir - red) / (nir + red + 1e-8)))
    health_score = round(
        0.35 * moisture_pct +
        0.25 * (organic_matter / 8 * 100) +
        0.25 * max(0, ndvi_mean * 100) +
        0.15 * 60,  # nitrogen baseline
        2
    )
    health_score = float(np.clip(health_score, 0, 100))

    grade = (
        "excellent" if health_score >= 80 else
        "good"      if health_score >= 65 else
        "fair"      if health_score >= 45 else
        "poor"      if health_score >= 25 else "critical"
    )

    moisture_status = (
        "optimal" if 35 < moisture_pct < 65 else
        "wet"     if moisture_pct >= 65 else "dry"
    )

    recommendations = []
    if moisture_status == "dry":
        recommendations.append("Irrigation required. Soil moisture critically low.")
    if organic_matter < 1.5:
        recommendations.append("Add organic compost to improve soil structure and fertility.")
    if health_score < 50:
        recommendations.append("Soil health is poor. Consider soil testing and balanced NPK application.")
    if not recommendations:
        recommendations.append("Soil conditions are satisfactory. Maintain current practices.")

    return {
        "field_name":         field_name,
        "moisture_level":     moisture_pct,
        "moisture_status":    moisture_status,
        "organic_matter":     organic_matter,
        "nitrogen_index":     round(40 + ndvi_mean * 30, 2),
        "phosphorus_index":   round(35 + brightness * 20, 2),
        "potassium_index":    round(45 + (1 - brightness) * 15, 2),
        "ph_estimate":        round(6.0 + (1 - brightness) * 1.5, 1),
        "salinity_index":     round(max(0, 20 - organic_matter * 2), 2),
        "erosion_risk":       round(max(0, 60 - health_score * 0.5), 2),
        "health_score":       health_score,
        "health_grade":       grade,
        "recommendations":    recommendations,
    }

@router.get("/demo-map")
async def get_demo_soil_map(current_user: User = Depends(get_current_user)):
    """Synthetic soil health grid for demo visualization."""
    import random, math
    random.seed(99)
    points = []
    for _ in range(150):
        lat = 20.5 + random.uniform(-0.25, 0.25)
        lon = 78.9 + random.uniform(-0.25, 0.25)
        score = max(20, min(95, 65 + random.gauss(0, 15)))
        points.append({
            "lat": round(lat, 6), "lon": round(lon, 6),
            "health_score": round(score, 1),
            "moisture": round(random.uniform(25, 75), 1),
            "grade": "good" if score >= 65 else "fair" if score >= 45 else "poor"
        })
    return {"points": points}
