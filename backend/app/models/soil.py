from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class SoilHealthGrade(str, enum.Enum):
    excellent = "excellent"
    good = "good"
    fair = "fair"
    poor = "poor"
    critical = "critical"

class SoilAnalysis(Base):
    __tablename__ = "soil_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("crop_analyses.id"), nullable=False)

    moisture_level = Column(Float, nullable=True)        # 0-100 %
    moisture_status = Column(String(50), nullable=True)  # dry / optimal / wet
    organic_matter = Column(Float, nullable=True)        # %
    nitrogen_index = Column(Float, nullable=True)        # 0-100
    phosphorus_index = Column(Float, nullable=True)      # 0-100
    potassium_index = Column(Float, nullable=True)       # 0-100
    ph_estimate = Column(Float, nullable=True)           # 4-9
    salinity_index = Column(Float, nullable=True)        # 0-100
    erosion_risk = Column(Float, nullable=True)          # 0-100
    compaction_index = Column(Float, nullable=True)      # 0-100
    health_score = Column(Float, nullable=True)          # 0-100
    health_grade = Column(Enum(SoilHealthGrade), nullable=True)
    spectral_features = Column(JSON, default={})
    recommendations = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    crop_analysis = relationship("CropAnalysis", back_populates="soil_analyses")
