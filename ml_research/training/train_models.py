#!/usr/bin/env python3
"""
AgriVision AI — Model Training Pipeline
========================================
Trains all three models:
  1. CropHealthCNN  (EfficientNetB0 transfer learning)
  2. CropStressLSTM (Bi-LSTM + Attention)
  3. PestRiskRF     (RandomForest)

Usage:
    python train_models.py --model all
    python train_models.py --model rf --synthetic   # fast demo (no images)
    python train_models.py --model lstm --synthetic
"""

import argparse
import numpy as np
import json
import os
from pathlib import Path

MODELS_DIR = Path("backend/app/ml/weights")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR   = Path("ml_research/datasets/synthetic")


# ─── RF Training ─────────────────────────────────────────────────────────────

def train_rf(synthetic: bool = True):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    import joblib

    print("\n🌲 Training PestRiskRF...")

    if synthetic:
        X = np.load(DATA_DIR / "pest_features.npy")
        y = np.load(DATA_DIR / "pest_labels.npy")
    else:
        raise NotImplementedError("Provide real dataset path")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"  Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["low","medium","high","critical"]))

    out = MODELS_DIR / "pest_risk_rf.pkl"
    joblib.dump(clf, out)
    print(f"  ✓ Saved → {out}")

    # Feature importances
    feat_names = ["temperature","humidity","rainfall_mm","wet_days","ndvi","savi","evi","soil_moisture"]
    importances = dict(zip(feat_names, clf.feature_importances_.tolist()))
    with open(MODELS_DIR / "rf_feature_importances.json", "w") as f:
        json.dump(importances, f, indent=2)

    return acc


# ─── LSTM Training ────────────────────────────────────────────────────────────

def train_lstm(synthetic: bool = True, epochs: int = 30):
    import tensorflow as tf
    from tensorflow.keras import layers, callbacks

    print("\n🔁 Training CropStressLSTM...")

    if synthetic:
        X = np.load(DATA_DIR / "lstm_features.npy")   # (500, 30, 8)
        y = np.load(DATA_DIR / "lstm_targets.npy")    # (500, 14, 3)
    else:
        raise NotImplementedError("Provide real dataset path")

    split = int(len(X) * 0.8)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    # Flatten targets for training: (batch, 14*3)
    y_train_flat = y_train.reshape(len(y_train), -1)
    y_val_flat   = y_val.reshape(len(y_val), -1)

    inp = tf.keras.Input(shape=(30, 8))
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(inp)
    x = layers.MultiHeadAttention(num_heads=4, key_dim=32)(x, x)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(14 * 3, activation="sigmoid")(x)

    model = tf.keras.Model(inp, out)
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.summary()

    cbs = [
        callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6),
        callbacks.ModelCheckpoint(str(MODELS_DIR / "lstm_best.h5"), save_best_only=True),
    ]

    history = model.fit(
        X_train, y_train_flat,
        validation_data=(X_val, y_val_flat),
        epochs=epochs,
        batch_size=32,
        callbacks=cbs,
        verbose=1,
    )

    final_mae = min(history.history["val_mae"])
    print(f"  Best Val MAE: {final_mae:.4f}")

    model.save(MODELS_DIR / "crop_stress_lstm.h5")
    print(f"  ✓ Saved → {MODELS_DIR}/crop_stress_lstm.h5")
    return final_mae


# ─── CNN Training ─────────────────────────────────────────────────────────────

def train_cnn(data_dir: str = None, epochs: int = 20):
    import tensorflow as tf
    from tensorflow.keras import layers, callbacks
    from tensorflow.keras.applications import EfficientNetB0

    print("\n🖼️  Training CropHealthCNN...")

    if data_dir is None:
        # Generate tiny synthetic image dataset for demo
        print("  No image data provided — generating minimal synthetic set...")
        n = 200
        X = np.random.rand(n, 224, 224, 3).astype(np.float32)
        y = np.random.randint(0, 4, n)
    else:
        from tensorflow.keras.preprocessing.image import ImageDataGenerator
        datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=15,
            horizontal_flip=True,
            vertical_flip=True,
            brightness_range=[0.8, 1.2],
            validation_split=0.2,
        )
        train_gen = datagen.flow_from_directory(
            data_dir, target_size=(224, 224), batch_size=32,
            class_mode="sparse", subset="training"
        )
        val_gen = datagen.flow_from_directory(
            data_dir, target_size=(224, 224), batch_size=32,
            class_mode="sparse", subset="validation"
        )

    base = EfficientNetB0(weights="imagenet", include_top=False, input_shape=(224,224,3))
    for layer in base.layers[:-30]:
        layer.trainable = False

    inp = tf.keras.Input(shape=(224, 224, 3))
    x = base(inp, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    out = layers.Dense(4, activation="softmax")(x)

    model = tf.keras.Model(inp, out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    if data_dir:
        model.fit(train_gen, validation_data=val_gen, epochs=epochs,
                  callbacks=[callbacks.EarlyStopping(patience=5, restore_best_weights=True)])
    else:
        # Quick synthetic pass
        X_val, y_val = X[:40], y[:40]
        X_tr, y_tr = X[40:], y[40:]
        model.fit(X_tr, y_tr, validation_data=(X_val, y_val),
                  epochs=3, batch_size=16, verbose=1)

    model.save(MODELS_DIR / "crop_health_cnn.h5")
    print(f"  ✓ Saved → {MODELS_DIR}/crop_health_cnn.h5")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["all", "rf", "lstm", "cnn"], default="rf")
    parser.add_argument("--synthetic", action="store_true", default=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--data-dir", type=str, default=None,
                        help="Path to PlantVillage dataset for CNN training")
    args = parser.parse_args()

    if args.model in ("all", "rf"):
        train_rf(synthetic=args.synthetic)

    if args.model in ("all", "lstm"):
        train_lstm(synthetic=args.synthetic, epochs=args.epochs)

    if args.model in ("all", "cnn"):
        train_cnn(data_dir=args.data_dir, epochs=args.epochs)

    print("\n✅ Training complete! Weights saved to:", MODELS_DIR)


if __name__ == "__main__":
    main()
