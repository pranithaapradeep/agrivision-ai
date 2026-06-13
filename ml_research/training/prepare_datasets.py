#!/usr/bin/env python3
"""
AgriVision AI — Dataset Preparation Guide & Downloader
=======================================================

Run this script to prepare all datasets needed for model training.

Datasets used:
1. Indian Pines Hyperspectral Dataset (Purdue)
2. PlantVillage Disease Dataset (Kaggle)
3. Sentinel-2 Sample Imagery (COPERNICUS)
4. Weather CSV (IMD / OpenWeatherMap)

Usage:
    python prepare_datasets.py --all
    python prepare_datasets.py --dataset indian_pines
    python prepare_datasets.py --dataset plantvillage
    python prepare_datasets.py --dataset synthetic  # fast demo data
"""

import os
import urllib.request
import zipfile
import numpy as np
import json
from pathlib import Path
import argparse

DATASETS_DIR = Path("ml_research/datasets")
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Indian Pines Hyperspectral Dataset
# ─────────────────────────────────────────────────────────────────────────────
"""
MANUAL DOWNLOAD INSTRUCTIONS (free, no login required):
---------------------------------------------------------
URL: http://www.ehu.eus/ccwintco/uploads/6/67/Indian_pines_corrected.mat
     http://www.ehu.eus/ccwintco/uploads/c/c4/Indian_pines_gt.mat

Place files in: ml_research/datasets/indian_pines/

Loading example:
    import scipy.io
    data = scipy.io.loadmat('Indian_pines_corrected.mat')
    X = data['indian_pines_corrected']   # shape: (145, 145, 200) — 200 bands
    y = scipy.io.loadmat('Indian_pines_gt.mat')['indian_pines_gt']  # (145, 145) labels

Classes: 16 land-cover types (corn, wheat, soybeans, grass, forest, etc.)
Resolution: 145×145 pixels, 200 spectral bands (400–2500 nm)
Use for: NDVI/SAVI/EVI extraction, vegetation stress classification
"""

INDIAN_PINES_URL_DATA = "http://www.ehu.eus/ccwintco/uploads/6/67/Indian_pines_corrected.mat"
INDIAN_PINES_URL_GT   = "http://www.ehu.eus/ccwintco/uploads/c/c4/Indian_pines_gt.mat"


def download_indian_pines():
    dest = DATASETS_DIR / "indian_pines"
    dest.mkdir(exist_ok=True)

    for url, fname in [
        (INDIAN_PINES_URL_DATA, "Indian_pines_corrected.mat"),
        (INDIAN_PINES_URL_GT,   "Indian_pines_gt.mat"),
    ]:
        fpath = dest / fname
        if fpath.exists():
            print(f"  ✓ {fname} already exists, skipping.")
            continue
        print(f"  ↓ Downloading {fname}...")
        try:
            urllib.request.urlretrieve(url, fpath)
            print(f"  ✓ {fname} saved ({fpath.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            print(f"    Manual URL: {url}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. PlantVillage Disease Dataset
# ─────────────────────────────────────────────────────────────────────────────
"""
KAGGLE DOWNLOAD INSTRUCTIONS:
-------------------------------
1. Install kaggle CLI: pip install kaggle
2. Set up API key: ~/.kaggle/kaggle.json
3. Run: kaggle datasets download -d abdallahalidev/plantvillage-dataset

OR use the Hugging Face mirror:
    pip install datasets
    from datasets import load_dataset
    ds = load_dataset("jlbaker61/plant-village", split="train")

Classes (38 total, mapped to our 4):
    Healthy           → class 0
    Early Stress      → class 1  (early blight, leaf scorch)
    Disease Risk      → class 2  (late blight, bacterial spot)
    Severe Stress     → class 3  (rust, mosaic virus, severe blight)

Preprocessing for CNN:
    - Resize to 224×224
    - Normalize to [0, 1]
    - Augment: horizontal/vertical flip, rotation ±15°, brightness ±0.2
"""

def generate_plantvillage_structure():
    """Create the expected directory structure for PlantVillage."""
    base = DATASETS_DIR / "plantvillage"
    classes = ["healthy", "early_stress", "disease_risk", "severe_stress"]
    for cls in classes:
        (base / "train" / cls).mkdir(parents=True, exist_ok=True)
        (base / "val" / cls).mkdir(parents=True, exist_ok=True)
        (base / "test" / cls).mkdir(parents=True, exist_ok=True)
    print(f"  ✓ PlantVillage directory structure created at {base}")
    print("    → Download images from Kaggle and place in respective class folders.")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Synthetic Demo Dataset (no download needed — for offline demos)
# ─────────────────────────────────────────────────────────────────────────────

def generate_synthetic_dataset(n_samples: int = 2000, seed: int = 42):
    """
    Generate synthetic tabular data for RF/LSTM training during demos.
    Features: [temperature, humidity, rainfall, wet_days, ndvi, savi, evi,
               soil_moisture, soil_organic, lat_encoded, lon_encoded]
    Target: risk_level (0=low, 1=medium, 2=high, 3=critical)
    """
    np.random.seed(seed)
    dest = DATASETS_DIR / "synthetic"
    dest.mkdir(exist_ok=True)

    # Pest Risk Dataset (RF training)
    n = n_samples
    temperature   = np.random.normal(28, 6, n).clip(15, 42)
    humidity      = np.random.normal(65, 15, n).clip(30, 98)
    rainfall      = np.random.exponential(5, n).clip(0, 50)
    wet_days      = np.random.randint(0, 14, n)
    ndvi          = np.random.normal(0.55, 0.2, n).clip(0.1, 0.9)
    savi          = ndvi * 0.85 + np.random.normal(0, 0.05, n)
    evi           = ndvi * 0.75 + np.random.normal(0, 0.05, n)
    soil_moisture = np.random.normal(0.35, 0.12, n).clip(0.05, 0.7)

    # Risk label: high temp + high humidity + low NDVI → higher risk
    risk_score = (
        (temperature - 15) / 27 * 0.3 +
        humidity / 100 * 0.3 +
        (1 - ndvi) * 0.25 +
        wet_days / 14 * 0.15
    )
    risk_score += np.random.normal(0, 0.08, n)
    risk_labels = np.digitize(risk_score, [0.3, 0.55, 0.75]).clip(0, 3)

    X = np.column_stack([temperature, humidity, rainfall, wet_days,
                         ndvi, savi, evi, soil_moisture])
    np.save(dest / "pest_features.npy", X.astype(np.float32))
    np.save(dest / "pest_labels.npy", risk_labels.astype(np.int64))

    # Time-series dataset for LSTM (30-day windows)
    n_series = 500
    series_len = 44  # 30 history + 14 forecast
    features = []
    targets = []

    for _ in range(n_series):
        base_stress = np.random.uniform(0.2, 0.8)
        t = np.arange(series_len)
        noise = np.random.normal(0, 0.05, series_len)
        stress = np.clip(base_stress + 0.02 * t / series_len + noise, 0, 1)

        # 8 features per timestep
        feat = np.column_stack([
            stress,
            stress * 0.9 + np.random.normal(0, 0.03, series_len),  # disease
            stress * 0.7 + np.random.normal(0, 0.04, series_len),  # pest
            np.random.normal(28, 4, series_len),     # temperature
            np.random.normal(65, 10, series_len),    # humidity
            np.random.normal(5, 3, series_len).clip(0), # rainfall
            np.random.normal(0.55, 0.1, series_len), # ndvi
            np.random.normal(0.35, 0.08, series_len), # soil moisture
        ])
        features.append(feat[:30])   # 30-day input
        targets.append(feat[30:, :3])  # 14-day forecast for 3 targets

    np.save(dest / "lstm_features.npy", np.array(features, dtype=np.float32))
    np.save(dest / "lstm_targets.npy",  np.array(targets,  dtype=np.float32))

    # Metadata
    meta = {
        "pest_dataset": {"samples": n, "features": 8, "classes": 4},
        "lstm_dataset": {"series": n_series, "lookback": 30, "forecast": 14, "targets": 3},
        "class_names": ["low", "medium", "high", "critical"],
        "feature_names": ["temperature", "humidity", "rainfall_mm", "wet_days",
                          "ndvi", "savi", "evi", "soil_moisture"],
    }
    with open(dest / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  ✓ Synthetic pest dataset: {n} samples → {dest}/pest_*.npy")
    print(f"  ✓ Synthetic LSTM dataset: {n_series} series → {dest}/lstm_*.npy")
    return dest


# ─────────────────────────────────────────────────────────────────────────────
# 4. Sentinel-2 Sample Download (COPERNICUS)
# ─────────────────────────────────────────────────────────────────────────────
"""
SENTINEL-2 DOWNLOAD GUIDE:
---------------------------
Option A — Copernicus Data Space (Free, no ESA login needed):
    1. Visit: https://dataspace.copernicus.eu/
    2. Search for Level-2A products over your field of interest
    3. Download .SAFE folders (~800 MB each)

Option B — sentinelsat Python library (automated):
    pip install sentinelsat geopandas
    
    from sentinelsat import SentinelAPI
    from datetime import date
    
    api = SentinelAPI('user', 'password', 'https://apihub.copernicus.eu/apihub')
    products = api.query(
        area='POLYGON((72 20, 78 20, 78 24, 72 24, 72 20))',  # Punjab/Haryana
        date=('20240101', '20240601'),
        platformname='Sentinel-2',
        producttype='S2MSI2A',
        cloudcoverpercentage=(0, 20)
    )
    api.download_all(products)

Option C — Google Earth Engine (recommended for hackathon):
    import ee
    ee.Initialize()
    
    image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate('2024-01-01', '2024-06-01') \
        .filterBounds(ee.Geometry.Point([75.8, 30.9]))  # Ludhiana, Punjab
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
        .first()
    
    # Export band composites
    bands = image.select(['B4', 'B8', 'B11', 'B12'])  # Red, NIR, SWIR1, SWIR2
    
Key Sentinel-2 bands for AgriVision:
    B2  = Blue  (490nm)
    B3  = Green (560nm)
    B4  = Red   (665nm)  ← used in NDVI
    B5  = Red Edge 1 (705nm)
    B8  = NIR   (842nm)  ← used in NDVI
    B8A = Narrow NIR (865nm)
    B11 = SWIR-1 (1610nm) ← soil moisture
    B12 = SWIR-2 (2190nm) ← soil moisture

NDVI  = (B8 - B4) / (B8 + B4)
SAVI  = ((B8 - B4) / (B8 + B4 + 0.5)) × 1.5
EVI   = 2.5 × (B8 - B4) / (B8 + 6×B4 - 7.5×B2 + 1)
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AgriVision AI Dataset Preparer")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dataset", choices=["indian_pines", "plantvillage", "synthetic", "sentinel2"])
    args = parser.parse_args()

    if args.all or args.dataset == "synthetic":
        print("\n📦 Generating synthetic demo dataset...")
        generate_synthetic_dataset()

    if args.all or args.dataset == "indian_pines":
        print("\n📦 Downloading Indian Pines Hyperspectral Dataset...")
        download_indian_pines()

    if args.all or args.dataset == "plantvillage":
        print("\n📦 Setting up PlantVillage directory structure...")
        generate_plantvillage_structure()

    if args.all or args.dataset == "sentinel2":
        print("\n📦 Sentinel-2 Setup:")
        print("  → See the docstring above for download instructions.")
        print("  → Recommended: Google Earth Engine (free, browser-based)")

    print("\n✅ Done! Check ml_research/datasets/")


if __name__ == "__main__":
    main()
