from datetime import datetime
from typing import List

from pydantic import BaseModel


class EventPoint(BaseModel):
    lat: float
    lng: float


class EventGeometry(BaseModel):
    points: List[EventPoint]
    length: float


class EventSerializer(BaseModel):
    _id: str
    type: str
    source: str
    sourceid: str
    description: str
    location: str
    geometry: List[EventGeometry]
    start: datetime
    end: datetime
    timestamp: datetime
