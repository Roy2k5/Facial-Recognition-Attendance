from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    LargeBinary,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./attendance.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    fullname = Column(String)
    embedding = Column(LargeBinary)  # Lưu numpy array dạng bytes
    photo_path = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True)
    fullname = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.now, index=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tạo tables
Base.metadata.create_all(bind=engine)
