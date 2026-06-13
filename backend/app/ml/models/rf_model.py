"""
Random Forest Pest Risk Assessment for AgriVision AI
Features: weather + NDVI + historical patterns
Output: Low / Medium / High / Critical risk + individual pest scores
"""
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PestRiskResult:
    overall_risk_score: float       # 0-100
    risk_level: str                 # low|medium|high|critical
    fungal_risk: float
    insect_risk: float
    bacterial_risk: float
    viral_risk: float
    top_threats: List[Dict]
    recommendations: List[str]
    feature_importance: Dict[str, float]

RISK_THRESHOLDS = {"low": 30, "medium": 60, "high": 80}
PEST_THREATS = {
    "fungal": ["Brown rust", "Powdery mildew", "Blast disease", "Leaf blight"],
    "insect": ["Aphids", "Stem borer", "Whitefly", "Thrips", "Armyworm"],
    "bacterial": ["Bacterial leaf blight", "Crown gall", "Soft rot"],
    "viral": ["Leaf curl virus", "Mosaic virus", "Yellow vein mosaic"],
}

class PestRiskRF:
    """
    Random Forest classifier for pest outbreak risk prediction.
    Trained on historical pest incidence + weather data for Indian crops.
    Falls back to rule-based scoring for hackathon demo.
    """

    FEATURES = [
        "temperature", "humidity", "rainfall_7d", "consecutive_wet_days",
        "wind_speed", "ndvi", "ndvi_trend_7d", "soil_moisture",
        "crop_age_days", "previous_pest_incidence"
    ]

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        if model_path:
            self._load_model(model_path)

    def _load_model(self, path: str):
        try:
            import joblib
            self.model = joblib.load(path)
        except Exception as e:
            print(f"[RF] Model load failed: {e}")

    def train(self, X: np.ndarray, y: np.ndarray, save_path: Optional[str] = None):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ))
        ])
        pipeline.fit(X, y)
        self.model = pipeline

        if save_path:
            import joblib
            joblib.dump(pipeline, save_path)
        return pipeline

    def predict(self, features: Dict) -> PestRiskResult:
        """
        features: dict with keys from FEATURES list.
        Returns PestRiskResult.
        """
        if self.model:
            return self._model_predict(features)
        return self._rule_based_predict(features)

    def _rule_based_predict(self, f: Dict) -> PestRiskResult:
        """
        Rule-based pest risk scoring using agronomic heuristics.
        Calibrated for Indian Kharif / Rabi season crops.
        """
        temp  = f.get("temperature", 25)
        humid = f.get("humidity", 60)
        rain  = f.get("rainfall_7d", 5)
        wet   = f.get("consecutive_wet_days", 0)
        ndvi  = f.get("ndvi", 0.5)
        soil_m = f.get("soil_moisture", 40)

        # Fungal risk — thrives in high humidity + warm temps
        fungal = (
            0.40 * min(humid / 100, 1.0) +
            0.25 * min(max(temp - 15, 0) / 20, 1.0) +
            0.20 * min(wet / 7, 1.0) +
            0.15 * min(rain / 50, 1.0)
        ) * 100

        # Insect risk — depends on temperature + crop vigor (NDVI proxy)
        insect = (
            0.35 * min(max(temp - 18, 0) / 17, 1.0) +
            0.30 * (1 - min(ndvi, 1.0)) +  # stressed crops = more insect damage
            0.20 * min(humid / 100, 1.0) +
            0.15 * f.get("previous_pest_incidence", 0.2)
        ) * 100

        # Bacterial risk — warm + wet conditions
        bacterial = (
            0.45 * min(humid / 100, 1.0) +
            0.30 * min(max(temp - 20, 0) / 15, 1.0) +
            0.25 * min(wet / 5, 1.0)
        ) * 100

        # Viral risk — transmitted by insects, indirect weather influence
        viral = (
            0.50 * min(insect / 100, 1.0) +
            0.30 * min(max(temp - 25, 0) / 10, 1.0) +
            0.20 * (1 - min(ndvi, 1.0))
        ) * 100

        overall = 0.35 * fungal + 0.35 * insect + 0.20 * bacterial + 0.10 * viral
        overall = round(float(np.clip(overall, 0, 100)), 2)

        risk_level = (
            "critical" if overall > 80 else
            "high"     if overall > 60 else
            "medium"   if overall > 30 else "low"
        )

        # Build top threats list
        scores = {"fungal": fungal, "insect": insect, "bacterial": bacterial, "viral": viral}
        top_threats = []
        for category, score in sorted(scores.items(), key=lambda x: -x[1])[:2]:
            if score > 30:
                for pest_name in PEST_THREATS[category][:2]:
                    top_threats.append({
                        "pest": pest_name,
                        "category": category,
                        "risk_score": round(score, 1),
                        "risk_level": "high" if score > 60 else "medium"
                    })

        recommendations = self._generate_recommendations(risk_level, scores)

        return PestRiskResult(
            overall_risk_score=overall,
            risk_level=risk_level,
            fungal_risk=round(fungal, 2),
            insect_risk=round(insect, 2),
            bacterial_risk=round(bacterial, 2),
            viral_risk=round(viral, 2),
            top_threats=top_threats,
            recommendations=recommendations,
            feature_importance={k: 0.0 for k in self.FEATURES},
        )

    def _generate_recommendations(
        self, risk_level: str, scores: Dict
    ) -> List[str]:
        recs = []
        if scores.get("fungal", 0) > 60:
            recs.append("Apply preventive fungicide (mancozeb or copper-based). Monitor closely for 3–5 days.")
        if scores.get("insect", 0) > 60:
            recs.append("Inspect field edges for early insect colonies. Consider neem oil spray.")
        if scores.get("bacterial", 0) > 50:
            recs.append("Avoid overhead irrigation. Apply copper oxychloride as precaution.")
        if risk_level in ("high", "critical"):
            recs.append("Schedule field visit within 24–48 hours. Contact local Krishi Vigyan Kendra (KVK).")
        if risk_level == "low":
            recs.append("Conditions favorable. Continue regular monitoring schedule.")
        if not recs:
            recs.append("Monitor conditions daily. Maintain field hygiene.")
        return recs

    def _model_predict(self, features: Dict) -> PestRiskResult:
        X = np.array([[features.get(f, 0.0) for f in self.FEATURES]])
        probs = self.model.predict_proba(X)[0]
        classes = self.model.classes_
        class_idx = int(np.argmax(probs))
        risk_level = classes[class_idx]
        score_map = {"low": 15, "medium": 50, "high": 75, "critical": 92}
        overall = float(score_map.get(risk_level, 50))
        # Use rule-based for individual sub-scores
        result = self._rule_based_predict(features)
        result.overall_risk_score = overall
        result.risk_level = risk_level
        return result
