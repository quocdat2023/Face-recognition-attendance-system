from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    name: str
    user_id: str
    images: str # JSON string of base64 images

class UserResponse(BaseModel):
    id: str
    name: str
    user_id: str
    registered_at: str
    image_url: Optional[str] = None
    num_encodings: int = 1
