from datetime import datetime
from pydantic import BaseModel


class EventPoint(BaseModel):
    lat: float
    lng: float


class EventGeometry(BaseModel):
    points: list[EventPoint]
    length: float


class EventSerializer(BaseModel):
    id: str
    type: str
    source: str
    sourceid: str
    description: str
    location: str
    geometry: list[EventGeometry]
    start: datetime
    end: datetime
    timestamp: datetime
