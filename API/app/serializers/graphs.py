from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel


class GraphSerializer(BaseModel):
    labels: List[datetime]
    events: Dict[str, List[int]]
    flow: Dict[str, List[float]]
    weather: Dict[str, List[float]]
