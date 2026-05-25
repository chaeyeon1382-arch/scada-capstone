from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    slave_id = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    received_at = Column(Float, nullable=True)


class RelayLog(Base):
    __tablename__ = "relay_log"

    id = Column(Integer, primary_key=True, index=True)
    slave_id = Column(Integer, nullable=False)
    target = Column(String, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    