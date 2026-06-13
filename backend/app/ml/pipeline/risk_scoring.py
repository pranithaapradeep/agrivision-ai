"""
Risk Scoring and Recommendation Engine for AgriVision AI
Aggregates CNN + RF + LSTM outputs into a unified risk score
and generates actionable advisory messages.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class AnalysisReport:
    field_name: str
    crop_type: str
    overall_health_score: float      # 0-100
    overall_risk_score: float        # 0-100
    health_status: str
    risk_level: str
    vegetation_summary: Dict
    soil_summary: Dict
    pest_summary: Dict
    forecast_summary: Dict
    alerts: List[Dict]
    recommendations: List[Dict]
    confidence: float

class RiskScoringEngine:
    """Combines all ML outputs into a unified risk assessment."""

    HEALTH_WEIGHTS = {"vegetation": 0.40, "soil": 0.30, "pest": 0.30}

    def compute_overall_health(
        self,
        veg_score: float,
        soil_score: float,
        pest_score: float,
    ) -> float:
        """Weighted average of all component scores."""
        return round(
            self.HEALTH_WEIGHTS["vegetation"] * veg_score +
            self.HEALTH_WEIGHTS["soil"]        * soil_score +
            self.HEALTH_WEIGHTS["pest"]        * (100 - pest_score),
            2
        )

    def classify_health_status(self, score: float) -> str:
        if score >= 70: return "healthy"
        if score >= 50: return "early_stress"
        if score >= 30: return "disease_risk"
        return "severe_stress"

    def classify_risk_level(self, score: float) -> str:
        if score >= 80: return "critical"
        if score >= 60: return "high"
        if score >= 30: return "medium"
        return "low"

    def generate_alerts(
        self,
        health_score: float,
        pest_risk: float,
        soil_score: float,
        ndvi_mean: float,
        forecast_trend: str,
    ) -> List[Dict]:
        alerts = []
        if pest_risk > 70:
            alerts.append({
                "type": "pest_risk",
                "severity": "critical" if pest_risk > 85 else "danger",
                "title": "High Pest Risk Detected",
                "message": f"Pest outbreak probability at {pest_risk:.0f}%. Immediate monitoring recommended.",
            })
        if health_score < 40:
            alerts.append({
                "type": "crop_stress",
                "severity": "danger",
                "title": "Severe Crop Stress",
                "message": f"Overall health score dropped to {health_score:.0f}/100. Check irrigation and nutrient supply.",
            })
        elif health_score < 60:
            alerts.append({
                "type": "crop_stress",
                "severity": "warning",
                "title": "Crop Stress Increasing",
                "message": f"Health score at {health_score:.0f}/100. Early intervention may prevent yield loss.",
            })
        if ndvi_mean < 0.25:
            alerts.append({
                "type": "disease_outbreak",
                "severity": "warning",
                "title": "Possible Disease Outbreak",
                "message": f"NDVI at {ndvi_mean:.2f} — low vegetation index may indicate disease spread.",
            })
        if soil_score < 40:
            alerts.append({
                "type": "soil_degradation",
                "severity": "warning",
                "title": "Soil Condition Deteriorating",
                "message": f"Soil health score at {soil_score:.0f}/100. Soil amendment may be required.",
            })
        if forecast_trend == "deteriorating":
            alerts.append({
                "type": "forecast",
                "severity": "info",
                "title": "Worsening Trend Forecast",
                "message": "14-day projection shows deteriorating crop conditions. Plan preventive action.",
            })
        return alerts

    def generate_recommendations(
        self,
        health_score: float,
        soil_score: float,
        pest_risk: float,
        ndvi_mean: float,
        humidity: float,
        temperature: float,
    ) -> List[Dict]:
        recs = []

        # Irrigation
        if soil_score < 50:
            recs.append({
                "category": "irrigation",
                "priority": "high",
                "title": "Irrigation Recommended",
                "description": "Soil moisture indicators suggest water deficit. Schedule irrigation within 24–48 hours.",
                "icon": "droplet",
            })

        # Disease monitoring
        if health_score < 55 or ndvi_mean < 0.3:
            recs.append({
                "category": "disease",
                "priority": "high" if health_score < 40 else "medium",
                "title": "Monitor Disease Symptoms",
                "description": "Inspect leaves for yellowing, spots, or lesions. Collect samples if symptoms found.",
                "icon": "search",
            })

        # Pest control
        if pest_risk > 50:
            recs.append({
                "category": "pest",
                "priority": "high" if pest_risk > 70 else "medium",
                "title": "Apply Pest Control Measures",
                "description": "Deploy integrated pest management. Consider bio-pesticides (neem, Bt) as first-line defense.",
                "icon": "shield",
            })

        # Soil treatment
        if soil_score < 60:
            recs.append({
                "category": "soil",
                "priority": "medium",
                "title": "Soil Treatment Suggested",
                "description": "Apply balanced NPK fertilizer. Consider organic compost to improve soil health score.",
                "icon": "layers",
            })

        # Favorable condition
        if health_score >= 70 and pest_risk < 30:
            recs.append({
                "category": "general",
                "priority": "low",
                "title": "Conditions Favorable",
                "description": "Current crop health is good. Maintain regular monitoring every 3–5 days.",
                "icon": "check-circle",
            })

        return recs
