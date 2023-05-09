from datetime import datetime
from pydantic import BaseModel


class FlowPoint(BaseModel):
    lat: float
    lng: float


class FlowGeometry(BaseModel):
    points: list[FlowPoint]
    length: float


class FlowSegment(BaseModel):
    geometry: list[FlowGeometry]
    jam_factor: float


class FlowSerializer(BaseModel):
    id: str
    source: str
    location: str
    avgspeed: float
    segments: list[FlowSegment]
    timestamp: datetime
