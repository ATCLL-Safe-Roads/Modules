from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel


class EventSchema(BaseModel):
    id: int
    type: str
    source: str
    sourceid: str
    description: str
    location: str
    geometry: list
    start: datetime
    end: datetime
    timestamp: datetime

    class Config:
        json_encoders = {ObjectId: str}


class FlowSchema(BaseModel):
    id: int
    source: str
    location: str
    avgspeed: float
    segments: list
    timestamp: datetime

    class Config:
        json_encoders = {ObjectId: str}
