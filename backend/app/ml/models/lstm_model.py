"""
LSTM Time-Series Forecasting for AgriVision AI
Forecasts:
  • Future crop stress index (7–14 days)
  • Disease probability trend
  • Pest outbreak likelihood
Input features:
  NDVI, EVI, SAVI, temperature, humidity, rainfall,
  soil_moisture, consecutive_wet_days
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

FORECAST_HORIZON = 14  # days
LOOKBACK_WINDOW  = 30  # days of history needed

@dataclass
class ForecastResult:
    metric: str
    current_value: float
    forecast_values: List[float]       # 14-day forecast
    forecast_dates: List[str]          # ISO date strings
    trend: str                         # improving | stable | deteriorating
    confidence_interval_upper: List[float]
    confidence_interval_lower: List[float]
    alert_triggered: bool
    alert_message: Optional[str]

class CropStressLSTM:
    """
    Bidirectional LSTM with attention for multi-step crop stress forecasting.
    Falls back to statistical trend extrapolation when model isn't loaded.
    """

    INPUT_FEATURES = [
        "ndvi", "evi", "savi", "temperature", "humidity",
        "rainfall_mm", "soil_moisture", "wet_days_consecutive",
    ]
    N_FEATURES = len(INPUT_FEATURES)

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        if model_path:
            self._load_model(model_path)

    def _load_model(self, path: str):
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(path)
        except Exception as e:
            print(f"[LSTM] Model load failed: {e} — fallback mode")

    def build_model(self) -> object:
        """
        Architecture: BiLSTM → Attention → Dense multi-output
        Outputs: [stress_score, disease_prob, pest_prob] for each forecast step
        """
        import tensorflow as tf
        from tensorflow.keras import layers, Model

        inputs = tf.keras.Input(shape=(LOOKBACK_WINDOW, self.N_FEATURES))

        # Bi-directional LSTM layers
        x = layers.Bidirectional(
            layers.LSTM(128, return_sequences=True, dropout=0.2, recurrent_dropout=0.1)
        )(inputs)
        x = layers.Bidirectional(
            layers.LSTM(64, return_sequences=True, dropout=0.2)
        )(x)

        # Self-attention
        attn = layers.MultiHeadAttention(num_heads=4, key_dim=16)(x, x)
        x = layers.Add()([x, attn])
        x = layers.LayerNormalization()(x)

        x = layers.GlobalAveragePooling1D()(x)
        x = layers.Dense(128, activation="relu")(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(64, activation="relu")(x)

        # Multi-output: predict FORECAST_HORIZON steps × 3 targets
        outputs = layers.Dense(FORECAST_HORIZON * 3, activation="sigmoid")(x)
        outputs = layers.Reshape((FORECAST_HORIZON, 3))(outputs)

        model = Model(inputs, outputs)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-3),
            loss="mse", metrics=["mae"]
        )
        self.model = model
        return model

    def forecast(
        self,
        history: List[Dict],
        target: str = "stress_score"
    ) -> ForecastResult:
        """
        history: list of dicts with INPUT_FEATURES keys, sorted chronologically.
        Returns ForecastResult with 14-day projections.
        """
        from datetime import date, timedelta

        if len(history) < 7:
            return self._statistical_forecast(history, target)

        if self.model:
            return self._model_forecast(history, target)
        return self._statistical_forecast(history, target)

    def _statistical_forecast(
        self, history: List[Dict], target: str
    ) -> ForecastResult:
        """
        Fallback: linear trend + seasonal noise extrapolation.
        Good enough for MVP demo.
        """
        from datetime import date, timedelta

        # Extract relevant signal
        values = []
        for h in history[-LOOKBACK_WINDOW:]:
            if target == "stress_score":
                # Invert NDVI as proxy for stress
                ndvi = h.get("ndvi", 0.5)
                values.append(float(np.clip(1.0 - ndvi, 0, 1) * 100))
            elif target == "disease_prob":
                humid = h.get("humidity", 50) / 100
                temp  = (h.get("temperature", 25) - 15) / 25
                values.append(float(np.clip(humid * 0.6 + temp * 0.4, 0, 1) * 100))
            else:
                values.append(float(h.get(target, 30)))

        if not values:
            values = [30.0]

        arr = np.array(values, dtype=np.float32)
        current = float(arr[-1])

        # Fit simple linear trend on last 14 data points
        window = arr[-14:] if len(arr) >= 14 else arr
        x = np.arange(len(window))
        slope = float(np.polyfit(x, window, 1)[0])

        # Generate forecast with trend + noise
        forecast_vals = []
        for i in range(1, FORECAST_HORIZON + 1):
            noise = np.random.normal(0, 2)
            val = np.clip(current + slope * i + noise, 0, 100)
            forecast_vals.append(round(float(val), 2))

        ci_upper = [min(v + 8, 100) for v in forecast_vals]
        ci_lower = [max(v - 8, 0)   for v in forecast_vals]

        today = date.today()
        dates = [(today + timedelta(days=i)).isoformat() for i in range(1, FORECAST_HORIZON + 1)]

        # Determine trend
        if slope > 2:   trend = "deteriorating"
        elif slope < -2: trend = "improving"
        else:            trend = "stable"

        alert = forecast_vals[-1] > 70
        return ForecastResult(
            metric=target,
            current_value=round(current, 2),
            forecast_values=forecast_vals,
            forecast_dates=dates,
            trend=trend,
            confidence_interval_upper=ci_upper,
            confidence_interval_lower=ci_lower,
            alert_triggered=alert,
            alert_message=(
                f"⚠️ {target.replace('_', ' ').title()} projected to reach "
                f"{forecast_vals[-1]:.0f}% in 14 days"
            ) if alert else None,
        )

    def _model_forecast(self, history: List[Dict], target: str) -> ForecastResult:
        """Use trained LSTM model for prediction."""
        from datetime import date, timedelta

        # Build feature matrix
        seq = []
        for h in history[-LOOKBACK_WINDOW:]:
            row = [h.get(f, 0.0) for f in self.INPUT_FEATURES]
            seq.append(row)

        # Pad if needed
        while len(seq) < LOOKBACK_WINDOW:
            seq.insert(0, seq[0])

        X = np.array(seq[-LOOKBACK_WINDOW:], dtype=np.float32)[np.newaxis]
        pred = self.model.predict(X, verbose=0)[0]  # (14, 3)

        target_idx = {"stress_score": 0, "disease_prob": 1, "pest_prob": 2}.get(target, 0)
        forecast_vals = [round(float(v * 100), 2) for v in pred[:, target_idx]]
        ci_upper = [min(v + 6, 100) for v in forecast_vals]
        ci_lower = [max(v - 6, 0)   for v in forecast_vals]

        today = date.today()
        dates = [(today + timedelta(days=i)).isoformat() for i in range(1, FORECAST_HORIZON + 1)]
        current = forecast_vals[0]

        trend_diff = forecast_vals[-1] - forecast_vals[0]
        trend = "deteriorating" if trend_diff > 5 else "improving" if trend_diff < -5 else "stable"

        alert = forecast_vals[-1] > 70
        return ForecastResult(
            metric=target,
            current_value=round(current, 2),
            forecast_values=forecast_vals,
            forecast_dates=dates,
            trend=trend,
            confidence_interval_upper=ci_upper,
            confidence_interval_lower=ci_lower,
            alert_triggered=alert,
            alert_message=f"⚠️ {target.replace('_', ' ').title()} forecasted high" if alert else None,
        )
