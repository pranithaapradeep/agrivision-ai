"""
Vegetation Index Computation Engine
Implements NDVI, SAVI, EVI for Sentinel-2 / Landsat band data.
Band nomenclature (Sentinel-2):
  B2=Blue, B3=Green, B4=Red, B8=NIR, B8A=Red-Edge, B11=SWIR1, B12=SWIR2
"""
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional
import warnings
warnings.filterwarnings("ignore")

@dataclass
class IndexResult:
    name: str
    mean: float
    min_val: float
    max_val: float
    std: float
    histogram: Dict[str, list]  # {"bins": [...], "counts": [...]}
    interpretation: str
    health_score: float         # 0-100 normalized

class VegetationIndexEngine:
    """Computes spectral vegetation indices from multi-band arrays."""

    # Soil adjustment factor for SAVI
    L_FACTOR = 0.5

    # EVI coefficients (Huete et al., 2002)
    EVI_G = 2.5
    EVI_C1 = 6.0
    EVI_C2 = 7.5
    EVI_L = 1.0

    @staticmethod
    def _safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
        """Division with zero-guard to avoid NaN propagation."""
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.where(denominator == 0, 0.0, numerator / denominator)
        return np.clip(result, -1.0, 1.0)

    def compute_ndvi(self, nir: np.ndarray, red: np.ndarray) -> IndexResult:
        """
        NDVI = (NIR - Red) / (NIR + Red)
        Range: -1 to 1
          < 0.1  → bare soil / water
          0.1–0.3 → sparse vegetation / stressed
          0.3–0.6 → moderate vegetation
          > 0.6  → dense healthy vegetation
        """
        ndvi = self._safe_divide(nir - red, nir + red)
        mean = float(np.nanmean(ndvi))
        bins, counts = np.histogram(ndvi[~np.isnan(ndvi)], bins=20, range=(-1, 1))

        # Health score: map mean NDVI [-1,1] → [0,100]
        health = float(np.clip((mean + 1) / 2 * 100, 0, 100))

        interp = (
            "Dense, healthy vegetation" if mean > 0.6 else
            "Moderate vegetation cover" if mean > 0.3 else
            "Sparse / stressed vegetation" if mean > 0.1 else
            "Bare soil, water, or no vegetation"
        )
        return IndexResult(
            name="NDVI", mean=round(mean, 4),
            min_val=round(float(np.nanmin(ndvi)), 4),
            max_val=round(float(np.nanmax(ndvi)), 4),
            std=round(float(np.nanstd(ndvi)), 4),
            histogram={"bins": bins.tolist(), "counts": counts.tolist()},
            interpretation=interp, health_score=round(health, 2)
        )

    def compute_savi(self, nir: np.ndarray, red: np.ndarray) -> IndexResult:
        """
        SAVI = ((NIR - Red) / (NIR + Red + L)) × (1 + L)
        Corrects NDVI for soil background reflectance.
        Especially useful for arid/semi-arid Indian conditions.
        """
        L = self.L_FACTOR
        savi = self._safe_divide(
            (nir - red) * (1 + L),
            nir + red + L
        )
        mean = float(np.nanmean(savi))
        bins, counts = np.histogram(savi[~np.isnan(savi)], bins=20, range=(-1, 1))
        health = float(np.clip((mean + 1) / 2 * 100, 0, 100))
        interp = (
            "Excellent soil-adjusted vegetation" if mean > 0.5 else
            "Moderate vegetation with soil influence" if mean > 0.2 else
            "Sparse vegetation or degraded soil"
        )
        return IndexResult(
            name="SAVI", mean=round(mean, 4),
            min_val=round(float(np.nanmin(savi)), 4),
            max_val=round(float(np.nanmax(savi)), 4),
            std=round(float(np.nanstd(savi)), 4),
            histogram={"bins": bins.tolist(), "counts": counts.tolist()},
            interpretation=interp, health_score=round(health, 2)
        )

    def compute_evi(
        self, nir: np.ndarray, red: np.ndarray, blue: np.ndarray
    ) -> IndexResult:
        """
        EVI = G × (NIR - Red) / (NIR + C1×Red - C2×Blue + L)
        Reduces atmospheric effects and canopy background noise.
        Better for high-biomass regions (Kharif crops, paddy fields).
        """
        G, C1, C2, L = self.EVI_G, self.EVI_C1, self.EVI_C2, self.EVI_L
        evi = self._safe_divide(
            G * (nir - red),
            nir + C1 * red - C2 * blue + L
        )
        evi = np.clip(evi, -1.0, 1.0)
        mean = float(np.nanmean(evi))
        bins, counts = np.histogram(evi[~np.isnan(evi)], bins=20, range=(-1, 1))
        health = float(np.clip((mean + 1) / 2 * 100, 0, 100))
        interp = (
            "High biomass, dense canopy" if mean > 0.4 else
            "Moderate biomass" if mean > 0.2 else
            "Low biomass or stressed canopy"
        )
        return IndexResult(
            name="EVI", mean=round(mean, 4),
            min_val=round(float(np.nanmin(evi)), 4),
            max_val=round(float(np.nanmax(evi)), 4),
            std=round(float(np.nanstd(evi)), 4),
            histogram={"bins": bins.tolist(), "counts": counts.tolist()},
            interpretation=interp, health_score=round(health, 2)
        )

    def compute_all(
        self,
        nir: np.ndarray,
        red: np.ndarray,
        blue: np.ndarray,
        green: Optional[np.ndarray] = None
    ) -> Dict[str, IndexResult]:
        """Compute all indices and return as dict."""
        return {
            "NDVI": self.compute_ndvi(nir, red),
            "SAVI": self.compute_savi(nir, red),
            "EVI": self.compute_evi(nir, red, blue),
        }

    def composite_health_score(self, indices: Dict[str, IndexResult]) -> float:
        """
        Weighted composite of all indices → single 0-100 health score.
        Weights based on reliability for Indian crop types.
        """
        weights = {"NDVI": 0.45, "SAVI": 0.30, "EVI": 0.25}
        score = sum(
            indices[k].health_score * w
            for k, w in weights.items()
            if k in indices
        )
        return round(score, 2)
