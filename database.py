"""
Database Models — SQLite + SQLAlchemy
Tables:
  - noaa_measurement : Each NOAA reading (Bz, speed, density etc.)
  - cme_event        : Each CME record from NASA
  - threat_history   : Combined threat level after each scan
"""

from sqlalchemy import (
    create_engine, Column, Integer, Float, String,
    DateTime, Boolean, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./solar.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Table 1: NOAA Measurements ─────────────────────────
class NoaaMeasurement(Base):
    __tablename__ = "noaa_measurement"

    id              = Column(Integer, primary_key=True, index=True)
    record_time     = Column(DateTime, default=datetime.utcnow, index=True)
    bz_gsm          = Column(Float, nullable=True)
    bt              = Column(Float, nullable=True)
    speed           = Column(Float, nullable=True)
    density         = Column(Float, nullable=True)
    bz_neg_duration = Column(Integer, default=0)     # minutes
    l1_delay_min    = Column(Float, nullable=True)   # minutes
    level           = Column(String(20), default="UNKNOWN")
    message         = Column(Text, nullable=True)


# ── Table 2: NASA CME Events ───────────────────────────
class CmeEvent(Base):
    __tablename__ = "cme_event"

    id                = Column(Integer, primary_key=True, index=True)
    record_time       = Column(DateTime, default=datetime.utcnow, index=True)
    cme_id            = Column(String(100), unique=True, index=True)
    speed             = Column(Float, nullable=True)
    half_angle        = Column(Float, nullable=True)
    longitude         = Column(Float, nullable=True)
    latitude          = Column(Float, nullable=True)
    alignment         = Column(String(20), nullable=True)   # DIRECT / EDGE / FAR
    level             = Column(String(20), default="LOW")
    earth_target      = Column(Boolean, default=False)
    estimated_arrival = Column(String(50), nullable=True)   # TRT format
    l1_delay          = Column(String(30), nullable=True)
    targets           = Column(Text, nullable=True)         # comma separated


# ── Table 3: Combined Threat History ─────────────────────
class ThreatHistory(Base):
    __tablename__ = "threat_history"

    id            = Column(Integer, primary_key=True, index=True)
    record_time   = Column(DateTime, default=datetime.utcnow, index=True)
    noaa_level    = Column(String(20), default="SAFE")
    cme_level     = Column(String(20), default="SAFE")
    final_level   = Column(String(20), default="SAFE")
    determiner    = Column(String(30), nullable=True)


def create_database():
    """Creates tables if they do not exist. Called at app startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Session factory for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
