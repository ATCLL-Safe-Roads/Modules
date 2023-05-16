from datetime import datetime
from typing import List

from pydantic import BaseModel


class FlowPoint(BaseModel):
    lat: float
    lng: float


class FlowGeometry(BaseModel):
    points: List[FlowPoint]
    length: float


class FlowSegment(BaseModel):
    geometry: List[FlowGeometry]
    jam_factor: float


class FlowSerializer(BaseModel):
    _id: str
    source: str
    location: str
    avgspeed: float
    segments: List[FlowSegment]
    timestamp: datetime
