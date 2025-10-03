from pydantic import BaseModel, Field
from typing import Optional

class AirQualityData(BaseModel):
    aqi: Optional[int] = Field(None, description="Air Quality Index (1-500)")
    pm25: Optional[float] = Field(None, description="µg/m³")
    pm10: Optional[float] = Field(None, description="µg/m³")
    o3: Optional[float] = Field(None, description="µg/m³")
    no2: Optional[float] = Field(None, description="µg/m³")
    so2: Optional[float] = Field(None, description="µg/m³")
    co: Optional[float] = Field(None, description="µg/m³")
    quality_level: Optional[str] = None
