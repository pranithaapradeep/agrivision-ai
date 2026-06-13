"""
CNN Disease Detection Model for AgriVision AI
Architecture: EfficientNetB0-based transfer learning
Classes: healthy | early_stress | disease_risk | severe_stress
"""
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional
import json
import os

# ── Class definitions ────────────────────────────────────────────────────────
CLASSES = ["healthy", "early_stress", "disease_risk", "severe_stress"]
CLASS_LABELS = {
    "healthy":      {"label": "Healthy Crop",    "color": "#22c55e", "score_range": (70, 100)},
    "early_stress": {"label": "Early Stress",    "color": "#eab308", "score_range": (45, 70)},
    "disease_risk": {"label": "Disease Risk",    "color": "#f97316", "score_range": (25, 45)},
    "severe_stress":{"label": "Severe Stress",   "color": "#ef4444", "score_range": (0, 25)},
}


class CropHealthCNN:
    """
    CNN classifier wrapping TensorFlow EfficientNetB0 for crop disease detection.
    Falls back to a rule-based heuristic if model weights aren't loaded yet
    (useful during hackathon demo before full training is complete).
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        """Try to load saved model; silently fall back to heuristic mode."""
        if not self.model_path or not Path(self.model_path).exists():
            return
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(self.model_path)
        except Exception as e:
            print(f"[CNN] Could not load model: {e} — using heuristic fallback")

    def build_model(self):
        """
        Build EfficientNetB0 transfer-learning model.
        Call this to create and train from scratch.
        """
        import tensorflow as tf
        from tensorflow.keras import layers, Model

        base = tf.keras.applications.EfficientNetB0(
            include_top=False,
            weights="imagenet",
            input_shape=(224, 224, 3),
            pooling="avg",
        )
        # Fine-tune last 30 layers
        for layer in base.layers[:-30]:
            layer.trainable = False

        inputs  = tf.keras.Input(shape=(224, 224, 3))
        x = tf.keras.applications.efficientnet.preprocess_input(inputs)
        x = base(x, training=False)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(256, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        outputs = layers.Dense(len(CLASSES), activation="softmax")(x)

        model = Model(inputs, outputs)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        self.model = model
        return model

    def predict(self, image_array: np.ndarray) -> Dict:
        """
        Predict crop health class from 224×224×3 float32 array.
        Returns dict with class, confidence, all probabilities.
        """
        if self.model is not None:
            return self._model_predict(image_array)
        return self._heuristic_predict(image_array)

    def _model_predict(self, image_array: np.ndarray) -> Dict:
        import tensorflow as tf
        batch = np.expand_dims(image_array, 0).astype(np.float32)
        probs = self.model.predict(batch, verbose=0)[0]
        idx = int(np.argmax(probs))
        return {
            "class": CLASSES[idx],
            "confidence": float(probs[idx]),
            "probabilities": {c: float(p) for c, p in zip(CLASSES, probs)},
            "source": "model",
        }

    def _heuristic_predict(self, image_array: np.ndarray) -> Dict:
        """
        Rule-based fallback using image greenness ratio.
        Green channel dominance ≈ healthy vegetation.
        """
        img = image_array
        if img.max() > 1.0:
            img = img / 255.0
        r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
        greenness = float(np.mean(g) / (np.mean(r) + np.mean(g) + np.mean(b) + 1e-8))

        if greenness > 0.40:
            idx, probs = 0, [0.80, 0.12, 0.05, 0.03]
        elif greenness > 0.33:
            idx, probs = 1, [0.15, 0.62, 0.18, 0.05]
        elif greenness > 0.26:
            idx, probs = 2, [0.05, 0.20, 0.60, 0.15]
        else:
            idx, probs = 3, [0.03, 0.07, 0.20, 0.70]

        return {
            "class": CLASSES[idx],
            "confidence": probs[idx],
            "probabilities": {c: p for c, p in zip(CLASSES, probs)},
            "source": "heuristic",
        }


class ModelTrainer:
    """Training utilities for the CNN model."""

    def get_data_augmentation(self):
        """Returns Keras augmentation pipeline for agricultural images."""
        import tensorflow as tf
        return tf.keras.Sequential([
            tf.keras.layers.RandomFlip("horizontal_and_vertical"),
            tf.keras.layers.RandomRotation(0.2),
            tf.keras.layers.RandomZoom(0.15),
            tf.keras.layers.RandomBrightness(0.2),
            tf.keras.layers.RandomContrast(0.2),
        ], name="augmentation")

    def train(
        self,
        model,
        train_ds,
        val_ds,
        epochs: int = 50,
        model_save_path: str = "/app/ml_models/cnn_crop_health.h5"
    ):
        import tensorflow as tf

        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                model_save_path, save_best_only=True,
                monitor="val_accuracy", mode="max", verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                patience=8, restore_best_weights=True, monitor="val_loss"
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                factor=0.5, patience=4, min_lr=1e-7
            ),
        ]
        history = model.fit(
            train_ds, validation_data=val_ds,
            epochs=epochs, callbacks=callbacks
        )
        return history
