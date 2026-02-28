from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime, date
import numpy as np
import cv2
import os
from typing import List
import pickle

from db.database import get_db, User, AttendanceRecord
from service import recognition_service, faiss_service
from schema.app_schema import UserResponse, AttendanceResponse
from core import settings

attendance_router = APIRouter(prefix="/api", tags=["attendance"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@attendance_router.post("/register")
async def register_user(
    fullname: str = Form(...),
    employee_id: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Register new user with face photo"""

    # Check if employee_id already exists
    existing_user = db.query(User).filter(User.employee_id == employee_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    # Read and decode image
    contents = await photo.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # Extract embedding
    embedding = recognition_service.extract_embedding(img)
    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected in image")

    # Save photo
    photo_path = os.path.join(UPLOAD_DIR, f"{employee_id}.jpg")
    cv2.imwrite(photo_path, img)

    # Save to database
    user = User(
        employee_id=employee_id,
        fullname=fullname,
        embedding=pickle.dumps(embedding),
        photo_path=photo_path,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Add to FAISS index
    faiss_service.add_embedding(employee_id, embedding)

    return {
        "success": True,
        "message": "User registered successfully",
        "employee_id": employee_id,
    }


@attendance_router.post("/attendance", response_model=AttendanceResponse)
async def check_attendance(
    image: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Check attendance by face recognition"""

    # Read and decode image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return AttendanceResponse(success=False, message="Invalid image")

    # Extract embedding
    embedding = recognition_service.extract_embedding(img)
    if embedding is None:
        return AttendanceResponse(success=False, message="No face detected")

    # Search in FAISS
    result = faiss_service.search(embedding, k=1)
    if result is None:
        return AttendanceResponse(success=False, message="No registered users found")

    employee_id, confidence = result

    # Check threshold
    if confidence < settings.threshold:
        return AttendanceResponse(
            success=False, message=f"Face not recognized (confidence: {confidence:.2f})"
        )

    # Get user info
    user = db.query(User).filter(User.employee_id == employee_id).first()
    if not user:
        return AttendanceResponse(success=False, message="User not found in database")

    # Check if already checked in today
    today = date.today()
    existing_record = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.timestamp >= datetime.combine(today, datetime.min.time()),
        )
        .first()
    )

    if existing_record:
        return AttendanceResponse(
            success=False,
            message="Already checked in today",
            employee_id=employee_id,
            name=user.fullname,
            confidence=confidence,
            timestamp=existing_record.timestamp,
        )

    # Create attendance record
    record = AttendanceRecord(
        employee_id=employee_id, fullname=user.fullname, confidence=confidence
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return AttendanceResponse(
        success=True,
        message="Attendance recorded successfully",
        employee_id=employee_id,
        name=user.fullname,
        confidence=confidence,
        timestamp=record.timestamp,
    )


@attendance_router.get("/history")
async def get_attendance_history(date: str = None, db: Session = Depends(get_db)):
    """Get attendance history, optionally filtered by date"""

    query = db.query(AttendanceRecord)

    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(
                AttendanceRecord.timestamp
                >= datetime.combine(filter_date, datetime.min.time()),
                AttendanceRecord.timestamp
                < datetime.combine(filter_date, datetime.max.time()),
            )
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

    records = query.order_by(AttendanceRecord.timestamp.desc()).all()

    return {
        "records": [
            {
                "employee_id": r.employee_id,
                "name": r.fullname,
                "confidence": r.confidence,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in records
        ]
    }


@attendance_router.post("/attendance/clear")
async def clear_today_attendance(db: Session = Depends(get_db)):
    """Clear today's attendance records"""

    today = date.today()
    deleted = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.timestamp >= datetime.combine(today, datetime.min.time())
        )
        .delete()
    )

    db.commit()

    return {"success": True, "message": f"Deleted {deleted} records"}


@attendance_router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get attendance statistics"""

    total_users = db.query(User).count()

    today = date.today()
    attended_today = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.timestamp >= datetime.combine(today, datetime.min.time())
        )
        .distinct(AttendanceRecord.employee_id)
        .count()
    )

    return {
        "total_users": total_users,
        "attended_today": attended_today,
        "absent_today": total_users - attended_today,
    }


@attendance_router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all registered users"""

    users = db.query(User).all()
    return users
