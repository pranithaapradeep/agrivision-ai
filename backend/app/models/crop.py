from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class HealthStatus(str, enum.Enum):
    healthy = "healthy"
    early_stress = "early_stress"
    disease_risk = "disease_risk"
    severe_stress = "severe_stress"

class CropAnalysis(Base):
    __tablename__ = "crop_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    field_name = Column(String(255), nullable=False)
    crop_type = Column(String(100), nullable=False)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)

    # Image refs
    satellite_image_path = Column(String(512), nullable=True)
    processed_image_path = Column(String(512), nullable=True)
    health_map_path = Column(String(512), nullable=True)

    # Scores
    overall_health_score = Column(Float, nullable=True)   # 0-100
    health_status = Column(Enum(HealthStatus), nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Metadata
    analysis_metadata = Column(JSON, default={})
    recommendations = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="analyses")
    vegetation_indices = relationship("VegetationIndex", back_populates="analysis", cascade="all, delete-orphan")
    pest_assessments = relationship("PestRiskAssessment", back_populates="crop_analysis", cascade="all, delete-orphan")
    soil_analyses = relationship("SoilAnalysis", back_populates="crop_analysis", cascade="all, delete-orphan")

class VegetationIndex(Base):
    __tablename__ = "vegetation_indices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("crop_analyses.id"), nullable=False)
    index_type = Column(String(20), nullable=False)   # NDVI, SAVI, EVI
    mean_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    std_value = Column(Float, nullable=True)
    pixel_distribution = Column(JSON, default={})  # histogram bins
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    analysis = relationship("CropAnalysis", back_populates="vegetation_indices")
