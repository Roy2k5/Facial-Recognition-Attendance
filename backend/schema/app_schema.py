from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    employee_id: str
    fullname: str


class UserResponse(BaseModel):
    id: int
    employee_id: str
    fullname: str
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    success: bool
    message: str = ""
    employee_id: str = ""
    name: str = ""
    confidence: float = 0.0
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
