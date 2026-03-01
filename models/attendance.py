from pydantic import BaseModel
from typing import Optional

class AttendanceRecord(BaseModel):
    id: str
    user_id: str
    name: str
    timestamp: str
    shift: int
    shift_name: str
    date: str
    confidence: float
    image_url: Optional[str] = None

class AttendanceQuery(BaseModel):
    limit: int = 100
    date: Optional[str] = None
    shift: Optional[int] = None
