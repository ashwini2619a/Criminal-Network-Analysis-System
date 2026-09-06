import enum
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AlertType(enum.Enum):
    INTRUSION = "INTRUSION"
    TRIPWIRE_BREACH = "TRIPWIRE_BREACH"
    ZONE_BREACH = "ZONE_BREACH"
    CRAWLING = "CRAWLING"
    LOITERING = "LOITERING"
    FACE_MATCH = "FACE_MATCH"
    ANPR_HIT = "ANPR_HIT"

class Severity(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CameraStatus(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class PersonCategory(enum.Enum):
    TERRORIST = "TERRORIST"
    SMUGGLER = "SMUGGLER"
    WANTED = "WANTED"

class AlertEvent(Base):
    __tablename__ = "alert_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bop_id = Column(String, nullable=False)
    camera_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    description = Column(String, nullable=True)
    sha256_hash = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    thumbnail_b64 = Column(String, nullable=True)
    track_id = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    synced_from_edge = Column(Boolean, default=False)

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bop_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    rtsp_url = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(Enum(CameraStatus), default=CameraStatus.OFFLINE)
    last_heartbeat = Column(DateTime, nullable=True)

class BOP(Base):
    __tablename__ = "bops"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    sector = Column(String, nullable=False)
    battalion = Column(String, nullable=False)

class WatchlistPerson(Base):
    __tablename__ = "watchlist_persons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    alias = Column(String, nullable=True)
    category = Column(Enum(PersonCategory), nullable=False)
    photo_b64 = Column(String, nullable=True)
    embedding_b64 = Column(String, nullable=True)

class WatchlistVehicle(Base):
    __tablename__ = "watchlist_vehicles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plate_number = Column(String, nullable=False)
    owner_name = Column(String, nullable=True)
    category = Column(Enum(PersonCategory), nullable=False)
    flagged_reason = Column(String, nullable=True)


DATABASE_URL = "sqlite+aiosqlite:///./ibvap_backend.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
