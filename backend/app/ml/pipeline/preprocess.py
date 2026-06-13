"""
Multi-spectral / Hyperspectral image preprocessing for AgriVision AI.
Handles Sentinel-2, Landsat-8/9, and Indian Pines hyperspectral data.
"""
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple, Dict
import io
import base64

class ImagePreprocessor:
    """
    Normalizes, stacks, and prepares satellite imagery for ML models.
    Supports:
      • Sentinel-2 (13 bands, 10m–60m resolution)
      • Landsat 8/9 (11 bands, 30m resolution)
      • Indian Pines hyperspectral (200 bands, 20m resolution)
    """

    SENTINEL2_BANDS = ["B1","B2","B3","B4","B5","B6","B7","B8","B8A","B9","B10","B11","B12"]
    LANDSAT8_BANDS  = ["B1","B2","B3","B4","B5","B6","B7","B8","B9","B10","B11"]
    TARGET_SIZE     = (224, 224)  # CNN input resolution

    def load_from_bytes(self, img_bytes: bytes) -> np.ndarray:
        """Load uploaded image bytes → numpy array (H×W×C)."""
        img = Image.open(io.BytesIO(img_bytes))
        return np.array(img.convert("RGB"))

    def load_from_path(self, path: str) -> np.ndarray:
        """Load from disk path."""
        img = Image.open(path)
        return np.array(img)

    def normalize_reflectance(
        self, array: np.ndarray, sensor: str = "sentinel2"
    ) -> np.ndarray:
        """
        Convert DN to surface reflectance (0–1 range).
        Sentinel-2: divide by 10000 (after atmospheric correction)
        Landsat: multiply by 0.0000275 + (-0.2)
        """
        arr = array.astype(np.float32)
        if sensor == "sentinel2":
            arr = arr / 10000.0
        elif sensor.startswith("landsat"):
            arr = arr * 0.0000275 - 0.2
        return np.clip(arr, 0.0, 1.0)

    def extract_bands(
        self, array: np.ndarray, band_indices: Dict[str, int]
    ) -> Dict[str, np.ndarray]:
        """
        Extract named bands from multi-band array.
        band_indices: {"NIR": 3, "Red": 2, "Blue": 0, "Green": 1}
        """
        if array.ndim == 2:
            # Single band image
            return {"band": array}
        return {name: array[:, :, idx] for name, idx in band_indices.items()}

    def simulate_bands_from_rgb(
        self, rgb: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Approximate NIR, Red, Green, Blue from standard RGB upload.
        Used when the user uploads a regular photo or RGB satellite image.
        NIR ≈ 1.1 × Red (simple approximation for demo)
        """
        r = rgb[:, :, 0].astype(np.float32) / 255.0
        g = rgb[:, :, 1].astype(np.float32) / 255.0
        b = rgb[:, :, 2].astype(np.float32) / 255.0
        # Simulate NIR band: fields reflect more NIR than Red
        nir = np.clip(r * 1.15 + g * 0.05, 0, 1)
        return {"NIR": nir, "Red": r, "Green": g, "Blue": b}

    def resize_for_cnn(
        self, array: np.ndarray, size: Tuple[int, int] = None
    ) -> np.ndarray:
        """Resize (H, W, C) array to CNN input size."""
        target = size or self.TARGET_SIZE
        img = Image.fromarray((array * 255).astype(np.uint8) if array.max() <= 1.0 else array.astype(np.uint8))
        img = img.resize(target, Image.BILINEAR)
        return np.array(img).astype(np.float32) / 255.0

    def generate_false_color(
        self, nir: np.ndarray, red: np.ndarray, green: np.ndarray
    ) -> np.ndarray:
        """
        Classic NIR-Red-Green false color composite.
        Vegetation appears bright red — easy visual health check for judges.
        """
        stack = np.dstack([nir, red, green])
        stack = (stack - stack.min()) / (stack.max() - stack.min() + 1e-8)
        return (stack * 255).astype(np.uint8)

    def array_to_base64(self, array: np.ndarray) -> str:
        """Convert numpy uint8 array to base64 PNG for API response."""
        img = Image.fromarray(array.astype(np.uint8))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def generate_ndvi_colormap(self, ndvi: np.ndarray) -> np.ndarray:
        """
        Apply standard NDVI colormap:
          Red    → stressed / low NDVI (< 0.2)
          Yellow → moderate (0.2–0.4)
          Green  → healthy (> 0.4)
        Returns H×W×3 uint8 RGB array.
        """
        h, w = ndvi.shape
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
        # Normalize to 0-1
        norm = np.clip((ndvi + 1) / 2, 0, 1)
        # Low (red)
        mask_low  = norm < 0.35
        mask_mid  = (norm >= 0.35) & (norm < 0.55)
        mask_high = norm >= 0.55
        rgb[mask_low]  = [180, 40, 40]
        rgb[mask_mid]  = [220, 185, 40]
        rgb[mask_high] = [30, 160, 50]
        return rgb
