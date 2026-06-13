from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class PestRiskAssessment(Base):
    __tablename__ = "pest_risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("crop_analyses.id"), nullable=False)

    overall_risk_score = Column(Float, nullable=True)   # 0-100
    risk_level = Column(Enum(RiskLevel), nullable=True)

    # Individual pest categories
    fungal_risk = Column(Float, nullable=True)
    insect_risk = Column(Float, nullable=True)
    bacterial_risk = Column(Float, nullable=True)
    viral_risk = Column(Float, nullable=True)

    # Environmental drivers
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    rainfall_7d = Column(Float, nullable=True)
    consecutive_wet_days = Column(Float, nullable=True)

    # Spatial
    affected_area_pct = Column(Float, nullable=True)
    hotspot_coordinates = Column(JSON, default=[])

    weather_data = Column(JSON, default={})
    top_threats = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    crop_analysis = relationship("CropAnalysis", back_populates="pest_assessments")
