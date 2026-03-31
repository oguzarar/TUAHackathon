"""
Database Models — SQLite + SQLAlchemy
Tables:
  - noaa_measurement : Each NOAA reading (Bz, speed, density etc.)
  - cme_event        : Each CME record from NASA
  - kp_index         : Planetary K-Index records from NOAA
  - solar_flare      : Solar flare records (X-ray bursts) from NASA
  - threat_history   : Combined threat level after each scan
"""

from sqlalchemy import (
    create_engine, event, Column, Integer, Float, String,
    DateTime, Boolean, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./solar.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

# Enable WAL mode for better concurrent access (prevents "database is locked")
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()

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
    estimated_arrival = Column(String(50), nullable=True)   # TSİ format
    l1_delay          = Column(String(30), nullable=True)
    targets           = Column(Text, nullable=True)         # comma separated


# ── Table 3: NOAA Kp Index ─────────────────────────────
class KpIndex(Base):
    __tablename__ = "kp_index"

    id          = Column(Integer, primary_key=True, index=True)
    record_time = Column(DateTime, default=datetime.utcnow, index=True)
    kp_value    = Column(Float, nullable=False)
    time_tag    = Column(String(50), nullable=True)
    level       = Column(String(20), default="SAFE")


# ── Table 4: NASA Solar Flares ─────────────────────────
class SolarFlare(Base):
    __tablename__ = "solar_flare"

    id          = Column(Integer, primary_key=True, index=True)
    record_time = Column(DateTime, default=datetime.utcnow, index=True)
    flare_id    = Column(String(100), unique=True, index=True)
    begin_time  = Column(String(50), nullable=True)
    peak_time   = Column(String(50), nullable=True)
    end_time    = Column(String(50), nullable=True)
    class_type  = Column(String(20), nullable=True) # e.g. M2.1, X1.0
    level       = Column(String(20), default="LOW")


# ── Table 5: Combined Threat History ─────────────────────
class ThreatHistory(Base):
    __tablename__ = "threat_history"

    id                  = Column(Integer, primary_key=True, index=True)
    record_time         = Column(DateTime, default=datetime.utcnow, index=True)
    noaa_level          = Column(String(20), default="SAFE")
    cme_level           = Column(String(20), default="SAFE")
    kp_level            = Column(String(20), default="SAFE")
    flare_level         = Column(String(20), default="SAFE")
    final_level         = Column(String(20), default="SAFE")        # Deprecated: Current consolidated level
    forecast_level      = Column(String(20), default="SAFE")        # New: 72-hour predicted threat
    forecast_description = Column(Text, nullable=True)               # New: Summary of why the forecast is X
    determiner          = Column(String(30), nullable=True)


# ── Table 6: Notification Log ────────────────────────────
class NotificationLog(Base):
    __tablename__ = "notification_log"

    id          = Column(Integer, primary_key=True, index=True)
    sent_at     = Column(DateTime, default=datetime.utcnow, index=True)
    event_id    = Column(String(100), index=True)   # CME ID or "noaa_spike_20260328"
    tier        = Column(Integer)                     # 1, 2, 3, 4
    channel     = Column(String(30), default="telegram")
    message     = Column(Text, nullable=True)
    success     = Column(Boolean, default=True)


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
