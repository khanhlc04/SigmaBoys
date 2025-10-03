from pydantic import BaseModel
from typing import Optional

class LocationData(BaseModel):
    lat: float
    lon: float
    city: Optional[str] = None
    country: Optional[str] = None