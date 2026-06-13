from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class AlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    danger = "danger"
    critical = "critical"

class AlertType(str, enum.Enum):
    pest_risk = "pest_risk"
    crop_stress = "crop_stress"
    disease_outbreak = "disease_outbreak"
    soil_degradation = "soil_degradation"
    weather_warning = "weather_warning"
    system = "system"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.warning)
    alert_type = Column(Enum(AlertType), nullable=False)
    field_name = Column(String(255), nullable=True)
    location_lat = Column(String(50), nullable=True)
    location_lon = Column(String(50), nullable=True)
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    metadata_ = Column("metadata", String(2048), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
