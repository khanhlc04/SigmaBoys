from pydantic import BaseModel, Field
from typing import Optional

class LightData(BaseModel):
    intensity: Optional[float] = Field(None, description="lux")
    uv_index: Optional[float] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    daylight_duration: Optional[float] = Field(None, description="hours")