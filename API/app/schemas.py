from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId


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
