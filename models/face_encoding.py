from pydantic import BaseModel

class FaceLocation(BaseModel):
    top: int
    right: int
    bottom: int
    left: int
    name: str
    confidence: float
    user_id: str = None
    status: str
    message: str
