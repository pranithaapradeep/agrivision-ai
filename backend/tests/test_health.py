"""
AgriVision AI — CI Smoke Tests
Validates core ML pipeline logic without requiring DB, Redis, or model weights.
"""
import pytest
import numpy as np


# ─── Vegetation Index Tests ───────────────────────────────────────────────────

def test_ndvi_output_shape_and_range():
    from app.ml.pipeline.vegetation_indices import VegetationIndexEngine
    engine = VegetationIndexEngine()
    nir = np.array([[0.8, 0.7], [0.6, 0.9]])
    red = np.array([[0.2, 0.3], [0.4, 0.1]])
    result = engine.compute_ndvi(nir, red)
    assert hasattr(result, "mean")
    assert -1.0 <= result.mean <= 1.0
    assert result.mean > 0  # NIR >> Red → positive NDVI


def test_savi_output():
    from app.ml.pipeline.vegetation_indices import VegetationIndexEngine
    engine = VegetationIndexEngine()
    nir = np.array([[0.8, 0.7]])
    red = np.array([[0.2, 0.3]])
    result = engine.compute_savi(nir, red)
    assert hasattr(result, "mean")
    assert -1.5 <= result.mean <= 1.5


def test_composite_health_score_range():
    from app.ml.pipeline.vegetation_indices import VegetationIndexEngine
    engine = VegetationIndexEngine()
    nir  = np.random.rand(10, 10) * 0.5 + 0.4
    red  = np.random.rand(10, 10) * 0.3
    blue = np.random.rand(10, 10) * 0.1
    indices = engine.compute_all(nir, red, blue)
    score = engine.composite_health_score(indices)
    assert 0.0 <= score <= 100.0


# ─── Risk Scoring Tests ───────────────────────────────────────────────────────

def test_health_status_classification():
    from app.ml.pipeline.risk_scoring import RiskScoringEngine
    engine = RiskScoringEngine()
    assert engine.classify_health_status(85) == "healthy"
    assert engine.classify_health_status(65) == "early_stress"
    assert engine.classify_health_status(45) == "disease_risk"
    assert engine.classify_health_status(25) == "severe_stress"


def test_risk_level_classification():
    from app.ml.pipeline.risk_scoring import RiskScoringEngine
    engine = RiskScoringEngine()
    assert engine.classify_risk_level(20) == "low"
    assert engine.classify_risk_level(45) == "medium"
    assert engine.classify_risk_level(70) == "high"
    assert engine.classify_risk_level(90) == "critical"


def test_overall_health_score():
    from app.ml.pipeline.risk_scoring import RiskScoringEngine
    engine = RiskScoringEngine()
    score = engine.compute_overall_health(
        veg_score=75.0,
        soil_score=60.0,
        pest_score=30.0,
    )
    assert isinstance(score, float)
    assert 0 <= score <= 100


def test_alert_generation_high_pest():
    from app.ml.pipeline.risk_scoring import RiskScoringEngine
    engine = RiskScoringEngine()
    alerts = engine.generate_alerts(
        health_score=45.0,
        pest_risk=85.0,
        soil_score=50.0,
        ndvi_mean=0.3,
        forecast_trend="declining",
    )
    assert isinstance(alerts, list)
    assert len(alerts) > 0
    # High pest risk (85) must trigger a pest alert
    assert any("pest" in a.get("type", "").lower() or "pest" in a.get("message", "").lower()
               for a in alerts)


def test_alert_generation_healthy_field():
    from app.ml.pipeline.risk_scoring import RiskScoringEngine
    engine = RiskScoringEngine()
    alerts = engine.generate_alerts(
        health_score=88.0,
        pest_risk=15.0,
        soil_score=80.0,
        ndvi_mean=0.75,
        forecast_trend="stable",
    )
    # Healthy field should have no critical alerts
    critical = [a for a in alerts if a.get("severity") == "critical"]
    assert len(critical) == 0


# ─── Security Tests ───────────────────────────────────────────────────────────

def test_password_hashing_and_verify():
    from app.core.security import get_password_hash, verify_password
    password = "SIH2024@AgriVision"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_jwt_token_created():
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": "test@agrivision.ai"})
    assert isinstance(token, str)
    assert len(token) > 20


# ─── Module Import Smoke Tests ────────────────────────────────────────────────

def test_all_core_imports():
    """If any import fails the CI immediately knows which module is broken."""
    from app.ml.models.rf_model import PestRiskRF
    from app.ml.models.cnn_model import CropHealthCNN
    from app.ml.models.lstm_model import CropStressLSTM
    from app.ml.pipeline.preprocess import ImagePreprocessor
    from app.ml.pipeline.vegetation_indices import VegetationIndexEngine
    from app.ml.pipeline.risk_scoring import RiskScoringEngine
    from app.core.config import settings
    from app.core.security import create_access_token, get_password_hash

    assert all([PestRiskRF, CropHealthCNN, CropStressLSTM,
                ImagePreprocessor, VegetationIndexEngine, RiskScoringEngine,
                settings, create_access_token, get_password_hash])
